import os
import sys
import secrets
from pathlib import Path

try:
    import pyodbc  # type: ignore
except Exception as e:
    print("pyodbc not installed in this environment:", e)
    sys.exit(1)


DB_NAME = os.getenv("DB_NAME", "EventTrackerDB_Dev")

SERVER_CANDIDATES = [
    os.getenv("DB_SERVER"),
    r"(localdb)\\MSSQLLocalDB",
    r"localhost\\SQLEXPRESS",
    r".\\SQLEXPRESS",
    r"localhost",
    r".",
]
SERVER_CANDIDATES = [s for s in SERVER_CANDIDATES if s]


def connect_any():
    last_err = None
    for server in SERVER_CANDIDATES:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={DB_NAME};Trusted_Connection=yes;"
        )
        try:
            cn = pyodbc.connect(conn_str, autocommit=True)
            print(f"Connected to SQL Server: server={server}, db={DB_NAME}")
            return cn, server
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Unable to connect to {DB_NAME}. Last error: {last_err}")


def table_exists(cur, name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", name
    )
    return cur.fetchone() is not None


def ensure_role_tables(cur):
    # Prefer singular PascalCase names
    if not table_exists(cur, "Role"):
        cur.execute(
            """
            CREATE TABLE Role (
              RoleID INT IDENTITY(1,1) PRIMARY KEY,
              Name NVARCHAR(64) NOT NULL UNIQUE,
              Description NVARCHAR(255) NULL,
              CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE()
            )
            """
        )
    # User table — avoid reserved keyword by bracketing
    if not table_exists(cur, "User") and not table_exists(cur, "[User]"):
        cur.execute(
            """
            CREATE TABLE [User] (
              UserID INT IDENTITY(1,1) PRIMARY KEY,
              Email NVARCHAR(256) NOT NULL UNIQUE,
              PasswordHash NVARCHAR(256) NULL,
              CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE()
            )
            """
        )
    if not table_exists(cur, "UserRole"):
        cur.execute(
            """
            CREATE TABLE UserRole (
              UserID INT NOT NULL,
              RoleID INT NOT NULL,
              PRIMARY KEY (UserID, RoleID),
              CONSTRAINT FK_UserRole_User FOREIGN KEY (UserID) REFERENCES [User](UserID),
              CONSTRAINT FK_UserRole_Role FOREIGN KEY (RoleID) REFERENCES Role(RoleID)
            )
            """
        )


def upsert_roles(cur):
    roles = [
        ("SystemAdmin", "Full platform administration"),
        ("Admin", "Organization administrator"),
        ("User", "Standard user")
    ]
    # Detect column names
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Role'")
    role_cols = {r[0].lower() for r in cur.fetchall()}
    name_col = 'Name' if 'name' in role_cols else 'RoleName'
    desc_col = 'Description' if 'description' in role_cols else 'RoleDescription'
    has_system = 'issystemrole' in role_cols
    has_createdby = 'createdby' in role_cols
    for name, desc in roles:
        cur.execute(f"SELECT RoleID FROM Role WHERE {name_col} = ?", name)
        row = cur.fetchone()
        if row is None:
            cols = [name_col, desc_col]
            vals = [name, desc]
            if has_system:
                cols.append("IsSystemRole")
                vals.append(1 if name == "SystemAdmin" else 0)
            if has_createdby:
                cols.append("CreatedBy")
                vals.append("SEED")
            # Permissions payload if supported
            if 'permissions' in role_cols:
                cols.append('Permissions')
                if name == 'SystemAdmin':
                    vals.append('{"all": true}')
                elif name == 'Admin':
                    vals.append('{"org_admin": true, "billing": true, "csv_export": true}')
                else:
                    vals.append('{"org_view": true, "edit_non_production": true}')
            placeholders = ", ".join(["?"] * len(vals))
            cur.execute(f"INSERT INTO Role ({', '.join(cols)}) VALUES ({placeholders})", *vals)
        else:
            # Update permissions if empty and column exists
            if 'permissions' in role_cols:
                if name == 'SystemAdmin':
                    perms = '{"all": true}'
                elif name == 'Admin':
                    perms = '{"org_admin": true, "billing": true, "csv_export": true}'
                else:
                    perms = '{"org_view": true, "edit_non_production": true}'
                cur.execute(f"UPDATE Role SET Permissions = COALESCE(NULLIF(Permissions, ''), ?) WHERE {name_col} = ?", perms, name)


def ensure_user_for_role(cur, email: str, role_name: str, password: str):
    # Ensure user
    cur.execute("SELECT UserID FROM [User] WHERE Email = ?", email)
    row = cur.fetchone()
    if row is None:
        # Determine org id
        cur.execute("SELECT TOP 1 OrganizationID FROM Organization ORDER BY OrganizationID")
        org_row = cur.fetchone()
        org_id = org_row[0] if org_row else None
        # Determine role id now
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Role'")
        role_cols = {r[0].lower() for r in cur.fetchall()}
        name_col = 'Name' if 'name' in role_cols else 'RoleName'
        cur.execute(f"SELECT RoleID FROM Role WHERE {name_col} = ?", role_name)
        role_id_insert = cur.fetchone()[0]
        # Generate salt+hash (simple SHA256)
        import hashlib, os as _os
        salt = secrets.token_hex(8)
        pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        base_username = email.split('@')[0]
        username = base_username
        # Ensure username uniqueness
        cur.execute("SELECT UserID FROM [User] WHERE Username = ?", username)
        if cur.fetchone() is not None:
            username = f"{base_username}{secrets.randbelow(10000)}"
        # Build dynamic insert based on available columns
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User'")
        user_cols = {r[0] for r in cur.fetchall()}
        cols = []
        vals = []
        def add(col, val):
            cols.append(col)
            vals.append(val)

        if 'OrganizationID' in user_cols:
            add('OrganizationID', org_id)
        add('RoleID', role_id_insert)
        add('Username', username)
        add('Email', email)
        if 'FirstName' in user_cols:
            add('FirstName', role_name)
        if 'LastName' in user_cols:
            add('LastName', 'User')
        add('PasswordHash', pwd_hash)
        if 'PasswordSalt' in user_cols:
            add('PasswordSalt', salt)
        if 'IsActive' in user_cols:
            add('IsActive', 1)
        if 'EmailVerified' in user_cols:
            add('EmailVerified', 1)
        if 'TwoFactorEnabled' in user_cols:
            add('TwoFactorEnabled', 0)
        if 'CreatedBy' in user_cols:
            add('CreatedBy', 'SEED')
        placeholders = ", ".join(["?"] * len(vals))
        cur.execute(f"INSERT INTO [User] ({', '.join(cols)}) VALUES ({placeholders})", *vals)
        # Fetch new ID
        try:
            cur.execute("SELECT SCOPE_IDENTITY()")
            user_id = int(float(cur.fetchone()[0]))
        except Exception:
            cur.execute("SELECT MAX(UserID) FROM [User]")
            user_id = int(cur.fetchone()[0])
    else:
        user_id = row[0]
    # Link role
    # Identify role id via name/rolename
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Role'")
    role_cols = {r[0].lower() for r in cur.fetchall()}
    name_col = 'Name' if 'name' in role_cols else 'RoleName'
    cur.execute(f"SELECT RoleID FROM Role WHERE {name_col} = ?", role_name)
    role_id = cur.fetchone()[0]
    # Set User.RoleID if present
    try:
        cur.execute("UPDATE [User] SET RoleID = ? WHERE UserID = ?", role_id, user_id)
    except Exception:
        pass
    cur.execute(
        "SELECT 1 FROM UserRole WHERE UserID = ? AND RoleID = ?", user_id, role_id
    )
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO UserRole (UserID, RoleID) VALUES (?, ?)", user_id, role_id
        )
    return user_id


def write_env_credentials(creds: dict):
    env_path = Path(".env.dev")
    if not env_path.exists():
        env_path = Path(".env")
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    kv = dict(
        SEED_SYSADMIN_EMAIL=creds["sysadmin"]["email"],
        SEED_SYSADMIN_PASSWORD=creds["sysadmin"]["password"],
        SEED_ADMIN_EMAIL=creds["admin"]["email"],
        SEED_ADMIN_PASSWORD=creds["admin"]["password"],
        SEED_USER_EMAIL=creds["user"]["email"],
        SEED_USER_PASSWORD=creds["user"]["password"],
    )
    # Update or append
    for k, v in kv.items():
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(k + "="):
                lines[i] = f"{k}={v}"
                updated = True
                break
        if not updated:
            lines.append(f"{k}={v}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated credentials in {env_path}")


def main():
    cn, server = connect_any()
    cur = cn.cursor()

    ensure_role_tables(cur)
    upsert_roles(cur)

    # Generate random passwords (dev only)
    creds = {
        "sysadmin": {
            "email": "sysadmin@local.dev",
            "password": secrets.token_urlsafe(16),
            "role": "SystemAdmin",
        },
        "admin": {
            "email": "admin@local.dev",
            "password": secrets.token_urlsafe(16),
            "role": "Admin",
        },
        "user": {
            "email": "user@local.dev",
            "password": secrets.token_urlsafe(16),
            "role": "User",
        },
    }

    for key, data in creds.items():
        user_id = ensure_user_for_role(cur, data["email"], data["role"], data["password"])
        print(f"Ensured {data['role']} user: {data['email']} (UserID={user_id})")

    write_env_credentials(creds)
    print("Provisioning complete.")


if __name__ == "__main__":
    main()
