# EventLeads - Event Form Builder

A full-stack application for creating and managing event registration forms with a visual form builder.

## Architecture

- **Backend**: FastAPI with SQLAlchemy, Alembic migrations, SQL Server
- **Frontend**: Next.js with TypeScript, Tailwind CSS, ShadCN UI
- **Database**: SQL Server with local development setup
- **Email**: MailHog for development email testing

## Quick Start

### Prerequisites

- **Python 3.11+** with virtual environment support
- **Node.js 18+** and npm
- **SQL Server** (local instance or Docker)
- **Docker Desktop** (for MailHog email testing)

### Environment Setup

1. **Copy environment file:**
   ```powershell
   Copy-Item ENV.sample .env.dev
   ```

2. **Update `.env.dev`** with your database connection details:
   ```env
   DATABASE_URL=mssql+pyodbc://@localhost/EventTrackerDB_Dev?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
   JWT_SECRET=your-secret-key
   ```

### Development Startup

**Option 1: Use the startup scripts (Recommended)**
```powershell
# Start all services
.\scripts\start-dev.ps1

# Stop all services
.\scripts\stop-dev.ps1
```

**Option 2: Manual startup**

1. **Start MailHog (email testing):**
   ```powershell
   docker-compose up -d mailhog
   ```

2. **Start Backend API:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Frontend (in new terminal):**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

### Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MailHog UI**: http://localhost:8025

## Project Structure

```
EventLeads/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Utilities (auth, security)
│   ├── migrations/         # Alembic database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities (API, auth)
│   └── package.json       # Node dependencies
├── scripts/               # PowerShell startup scripts
├── docs/                  # Documentation
└── docker-compose.yml     # Docker services
```

## Features

### ✅ Implemented
- **Authentication System**: User registration, login, email verification, password reset
- **Database Schema**: Complete auth tables and event management
- **API Endpoints**: Full CRUD operations for events, forms, leads
- **Frontend Components**: Login, signup, form builder UI
- **Development Tools**: PowerShell scripts, Docker setup, email testing

### 🔄 In Progress
- **Visual Form Builder**: Drag-and-drop form creation
- **Event Management**: Full event lifecycle
- **Lead Management**: Registration and tracking

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/verify` - Email verification
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/reset/request` - Request password reset
- `POST /api/auth/reset/confirm` - Confirm password reset

### Events
- `GET /api/events` - List events
- `POST /api/events` - Create event
- `GET /api/events/{id}` - Get event details
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event

## Database

The application uses SQL Server with the following key tables:
- `User` - User accounts and authentication
- `Organization` - Multi-tenant organization structure
- `Role` - Role-based access control
- `Event` - Event management
- `Form` - Dynamic form definitions
- `Lead` - Event registrations and leads

## Development Notes

### Known Issues
- Backend startup requires manual intervention due to module import issues
- Some migration files have SQL syntax issues that need fixing
- PowerShell scripts need refinement for robust startup

### Troubleshooting

**Backend won't start:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Database connection issues:**
- Verify SQL Server is running
- Check `DATABASE_URL` in `.env.dev`
- Ensure ODBC Driver 17 is installed

**Frontend build issues:**
```powershell
cd frontend
npm install
npm run build
```

## Contributing

1. Follow the BMAD architecture patterns
2. Update documentation in `docs/` folder
3. Run tests before submitting changes
4. Use conventional commit messages

## License

Private project - All rights reserved.
