# Environment Setup Guide

## Security Notice
**⚠️ CRITICAL: This repository is public. Never commit passwords or secrets to version control.**

## Environment Configuration

### 1. Create `.env.dev` file
Create a `.env.dev` file in the project root with the following content:

```bash
# EventLeads Development Environment Configuration
# DO NOT COMMIT PASSWORDS TO PUBLIC REPOSITORY

# Database Configuration
DATABASE_URL=mssql+pyodbc://@localhost/EventTrackerDB_Dev?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# Authentication
JWT_SECRET=your_secure_jwt_secret_here_change_this_in_production

# Email Configuration (MailHog for development)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=dev@eventleads.local

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Stripe (for future billing features)
STRIPE_SECRET_KEY=sk_test_replace_with_your_test_key

# Test User Credentials (DO NOT COMMIT TO PUBLIC REPO)
# These should be set locally for UAT testing only
# SEED_SYSADMIN_EMAIL=sysadmin@local.dev
# SEED_SYSADMIN_PASSWORD=your_test_password_here
# SEED_ADMIN_EMAIL=admin@local.dev
# SEED_ADMIN_PASSWORD=your_test_password_here
# SEED_USER_EMAIL=user@local.dev
# SEED_USER_PASSWORD=your_test_password_here
```

### 2. Test User Setup
For UAT testing, you can create test users using the provisioning script:

```bash
cd backend
python scripts/provision_roles_users.py
```

This will create test users in the database with the following credentials:

- **SystemAdmin**: `sysadmin@local.dev` / `[generated_password]`
- **Admin**: `admin@local.dev` / `[generated_password]`
- **User**: `user@local.dev` / `[generated_password]`

### 3. Security Best Practices

1. **Never commit `.env.dev`** - It's in `.gitignore`
2. **Use strong JWT secrets** - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **Rotate test passwords regularly**
4. **Use different credentials for production**

### 4. Database Setup

The application uses SQL Server with Windows Authentication:
- Server: `localhost`
- Database: `EventTrackerDB_Dev`
- Authentication: Windows (Trusted Connection)

### 5. Development Services

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **MailHog Web UI**: http://localhost:8025
- **MailHog SMTP**: localhost:1025

## UAT Testing Credentials

For User Acceptance Testing, use these standard test accounts:

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| SystemAdmin | sysadmin@local.dev | TestPassword123! | Full platform access |
| Admin | admin@local.dev | TestPassword123! | Organization admin |
| User | user@local.dev | TestPassword123! | Standard user |

**Note**: These are development-only credentials. Never use in production.
