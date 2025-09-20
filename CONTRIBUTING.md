# Contributing

Workflow (BMAD): PRD → Story → Migration → Code → Tests → Review → Deploy

Requirements
- Cite shard sections in PR description (e.g., 02-data-schema: Constraints)
- Any model change requires Alembic migration + rollback

Setup
- Backend: see backend/README or ARCHITECTURE.md
- Frontend: Next.js app in ./frontend

Testing
- Run unit tests and Alembic `upgrade head` in CI

## Getting Started

1. **Clone the repository**: `git clone <repository-url>`
2. **Set up the backend**:
   - Navigate to the `backend` directory: `cd backend`
   - Create and activate a virtual environment.
   - Install dependencies: `pip install -r requirements.txt`
3. **Set up the frontend**:
   - Navigate to the `frontend` directory: `cd frontend`
   - Install dependencies: `npm install`
4. **Configure your environment**:
   - Copy `ENV.sample` to `.env.dev` and update the database connection string.

Refer to `docs/environment-setup.md` for detailed instructions.

## Naming Conventions

To maintain consistency and prevent common errors, please adhere to the following naming conventions:

-   **Database (SQL Server)**: Use `PascalCase` for all tables and columns (e.g., `TableName`, `ColumnName`). This is the standard for this project's database schema.
-   **Backend (Python/SQLAlchemy)**:
    -   Use `snake_case` for variables, functions, and modules (e.g., `variable_name`, `function_name`).
    -   When writing raw SQL queries, remember to use the database's `PascalCase` for table and column names.
-   **Frontend (TypeScript/React)**: Use `camelCase` for variables and functions (e.g., `variableName`, `functionName`), and `PascalCase` for components (e.g., `ComponentName`).

## Submitting Changes

1.  Create a new branch for your feature or bug fix.



