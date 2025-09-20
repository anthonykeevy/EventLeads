import sys
from os.path import abspath, dirname, join

# Add the project's backend directory to the Python path
project_root = dirname(dirname(abspath(__file__)))
sys.path.insert(0, join(project_root, 'backend'))

from sqlalchemy import text
from app.core.db import engine


def cleanup_user(email: str):
    """
    Deletes a user and their associated email verification tokens from the database.
    """
    with engine.begin() as conn:
        # Find the user ID
        user_row = conn.execute(
            text("SELECT UserID FROM [User] WHERE Email = :email"), {"email": email}
        ).first()

        if not user_row:
            print(f"User with email '{email}' not found.")
            return

        user_id = user_row[0]
        print(f"Found user '{email}' with UserID: {user_id}. Cleaning up...")

        # Delete associated email verification tokens
        token_delete_result = conn.execute(
            text("DELETE FROM emailverificationtoken WHERE UserID = :user_id"),
            {"user_id": user_id},
        )
        print(f"Deleted {token_delete_result.rowcount} verification token(s).")

        # Delete the user
        user_delete_result = conn.execute(
            text("DELETE FROM [User] WHERE UserID = :user_id"), {"user_id": user_id}
        )
        print(f"Deleted {user_delete_result.rowcount} user record(s).")

        print("Cleanup complete.")


if __name__ == "__main__":
    target_email = "ant@keevy.com"
    if len(sys.argv) > 1:
        target_email = sys.argv[1]
    
    print(f"Attempting to clean up user: {target_email}")
    cleanup_user(target_email)
