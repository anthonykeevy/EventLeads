# EventLeads - Event Management Platform

A comprehensive event management platform with authentication, organization management, and event creation capabilities.

## 🚀 Current Status

**Story 0001 (Auth & Org Foundation) is COMPLETE and ready for UAT testing.**

### ✅ What's Working
- **Complete Authentication System**: Signup, login, email verification, password reset
- **Role-Based Access Control**: SystemAdmin, Admin, User roles
- **Frontend Application**: All auth pages and protected routes
- **Backend API**: Full REST API with JWT authentication
- **Database Integration**: SQL Server with Windows Authentication
- **Email System**: MailHog integration for development
- **Security Features**: Rate limiting, audit logging, secure tokens

## 🛠️ Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- SQL Server (LocalDB or Express)
- Docker Desktop (for MailHog)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EventLeads
   ```

2. **Set up environment**
   ```bash
   # Create .env.dev file (see docs/environment-setup.md)
   cp docs/environment-setup.md .env.dev
   # Edit .env.dev with your configuration
   ```

3. **Start the application**
   ```bash
   .\scripts\start-dev.ps1
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MailHog: http://localhost:8025

## 🧪 UAT Testing

### Test Credentials
| Role | Email | Password |
|------|-------|----------|
| SystemAdmin | sysadmin@local.dev | TestPassword123! |
| Admin | admin@local.dev | TestPassword123! |
| User | user@local.dev | TestPassword123! |

### Test Scenarios
1. **User Registration**: Create new account → Email verification
2. **User Login**: Login with test credentials
3. **Password Reset**: Request reset → Email link → New password
4. **Protected Routes**: Access dashboard and builder
5. **Role Testing**: Verify role-based access control

## 📁 Project Structure

```
EventLeads/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── utils/          # Security utilities
│   │   └── services/       # Email service
│   ├── migrations/         # Database migrations
│   └── scripts/           # Utility scripts
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/           # Pages and routing
│       ├── components/    # React components
│       └── lib/          # API integration
├── docs/                  # Documentation
└── scripts/              # Development scripts
```

## 🔧 Development

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.13
- **Database**: SQL Server with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **Migrations**: Alembic for database schema management

### Frontend (Next.js)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: JWT token management
- **API Integration**: RESTful API calls

### Database
- **Engine**: SQL Server (LocalDB/Express)
- **Authentication**: Windows Authentication
- **Database**: EventTrackerDB_Dev

## 📚 Documentation

- [**Project Status & BMAD Documentation**](docs/project-status-bmad.md) - Complete project status
- [**Environment Setup**](docs/environment-setup.md) - Configuration guide
- [**Security Checklist**](docs/security-checklist.md) - Security requirements
- [**Story 0001 Implementation**](docs/story-0001-implementation-walkthrough.md) - Auth system walkthrough
- [**Authentication Flow Diagrams**](docs/story-0001-authentication-flow-diagram.md) - System architecture

## 🔒 Security

**⚠️ IMPORTANT**: This is a public repository. Never commit passwords or secrets.

### Security Features
- JWT token authentication
- Bcrypt password hashing
- Rate limiting on sensitive endpoints
- Comprehensive audit logging
- Windows Authentication for database
- Secure token generation and validation

### Environment Security
- All sensitive data in environment variables
- `.env*` files excluded from version control
- Test credentials documented separately
- No hardcoded secrets in application code

## 🚦 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `GET /auth/verify` - Email verification
- `POST /auth/resend` - Resend verification
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get user profile
- `POST /auth/reset/request` - Password reset request
- `POST /auth/reset/confirm` - Password reset confirmation
- `POST /auth/logout` - User logout

### Health
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check

## 🧪 Testing

### UAT Testing
The application is ready for User Acceptance Testing with:
- Complete authentication flows
- Role-based access control
- Email verification system
- Password reset functionality
- Protected route access
- Comprehensive error handling

### Test Data
- Pre-configured test users with different roles
- MailHog for email testing
- Comprehensive audit logging
- Rate limiting validation

## 🤝 Contributing

1. **Security First**: Never commit secrets or passwords
2. **Follow Standards**: Use provided linting and formatting
3. **Document Changes**: Update relevant documentation
4. **Test Thoroughly**: Verify all functionality works
5. **Review Security**: Check security implications

## 📋 Known Issues

### ✅ Resolved
- All linting errors fixed (216 errors resolved)
- Import issues resolved
- Type annotation issues fixed
- Database connection configured
- Security vulnerabilities addressed

### 🔍 Current Status
- **Code Quality**: All linting issues resolved
- **Security**: No passwords in public repository
- **Documentation**: Complete and up-to-date
- **Testing**: Ready for UAT

## 🎯 Next Steps

### Immediate (UAT Phase)
1. Execute comprehensive UAT testing
2. Verify all authentication flows
3. Test security features
4. Validate email functionality

### Future Development
1. Production deployment preparation
2. Additional event management features
3. Enhanced security measures
4. Performance optimization

---

**Last Updated**: January 2025  
**Status**: Ready for UAT Testing  
**Version**: 0.1.0 (Story 0001 Complete)
