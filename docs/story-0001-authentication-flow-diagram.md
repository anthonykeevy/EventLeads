# Story 0001 - Authentication Flow & Services Diagram

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        A[Login Page] --> B[Signup Page]
        B --> C[Verify Page]
        C --> D[Dashboard]
        D --> E[Builder]
        E --> F[Reset Request]
        F --> G[Reset Confirm]
    end
    
    subgraph "Backend (FastAPI)"
        H[Auth Router] --> I[Security Utils]
        I --> J[JWT Service]
        H --> K[Email Service]
        H --> L[Database Service]
    end
    
    subgraph "Database (SQL Server)"
        M[User Table]
        N[EmailVerificationToken]
        O[PasswordResetToken]
        P[AuthEvent]
        Q[Organization]
    end
    
    subgraph "External Services"
        R[MailHog SMTP]
        S[Email Templates]
    end
    
    A --> H
    B --> H
    C --> H
    F --> H
    G --> H
    
    H --> M
    H --> N
    H --> O
    H --> P
    H --> Q
    
    K --> R
    R --> S
    
    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#e1f5fe
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#fff3e0
    style G fill:#fff3e0
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style J fill:#f3e5f5
    style K fill:#f3e5f5
    style L fill:#f3e5f5
    style M fill:#e3f2fd
    style N fill:#e3f2fd
    style O fill:#e3f2fd
    style P fill:#e3f2fd
    style Q fill:#e3f2fd
    style R fill:#fff8e1
    style S fill:#fff8e1
```

## Authentication Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant E as Email Service
    
    Note over U,E: User Registration Flow
    U->>F: Submit signup form
    F->>B: POST /auth/signup
    B->>DB: Create user (unverified)
    B->>DB: Create verification token
    B->>E: Send verification email
    E->>U: Email with verification link
    B->>F: "verification_required"
    F->>U: Show success message
    
    Note over U,E: Email Verification Flow
    U->>F: Click verification link
    F->>B: GET /auth/verify?token=...
    B->>DB: Validate token
    B->>DB: Mark user as verified
    B->>DB: Consume token
    B->>F: "verified"
    F->>U: Show verification success
    
    Note over U,E: Login Flow
    U->>F: Submit login form
    F->>B: POST /auth/login
    B->>DB: Validate credentials
    B->>DB: Check email verification
    B->>B: Generate JWT token
    B->>F: Return JWT token
    F->>F: Store token in localStorage
    F->>U: Redirect to dashboard
    
    Note over U,E: Protected Route Access
    U->>F: Access protected route
    F->>B: GET /auth/me (with JWT)
    B->>B: Validate JWT token
    B->>F: Return user profile
    F->>U: Show protected content
```

## Password Reset Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant E as Email Service
    
    Note over U,E: Password Reset Request
    U->>F: Request password reset
    F->>B: POST /auth/reset/request
    B->>DB: Check if user exists
    B->>DB: Create reset token
    B->>E: Send reset email
    E->>U: Email with reset link
    B->>F: "sent" (always 200)
    F->>U: Show confirmation message
    
    Note over U,E: Password Reset Confirmation
    U->>F: Click reset link
    F->>B: POST /auth/reset/confirm
    B->>DB: Validate reset token
    B->>DB: Update password hash
    B->>DB: Consume reset token
    B->>F: "updated"
    F->>U: Show success message
    F->>F: Redirect to login
```

## Security & Audit Flow

```mermaid
graph LR
    subgraph "Security Layer"
        A[Rate Limiting] --> B[JWT Validation]
        B --> C[Password Hashing]
        C --> D[Token Security]
    end
    
    subgraph "Audit System"
        E[Auth Events] --> F[Request Tracking]
        F --> G[IP/UserAgent Logging]
        G --> H[Audit Database]
    end
    
    subgraph "Database Tables"
        I[AuthEvent Table]
        J[User Table]
        K[Token Tables]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> I
    F --> I
    G --> I
    H --> I
    
    style A fill:#ffebee
    style B fill:#ffebee
    style C fill:#ffebee
    style D fill:#ffebee
    style E fill:#e8f5e8
    style F fill:#e8f5e8
    style G fill:#e8f5e8
    style H fill:#e8f5e8
    style I fill:#e3f2fd
    style J fill:#e3f2fd
    style K fill:#e3f2fd
```

## Service Dependencies

```mermaid
graph TD
    subgraph "Core Services"
        A[FastAPI Backend<br/>Port 8000]
        B[Next.js Frontend<br/>Port 3000]
        C[SQL Server Database<br/>Port 1433]
    end
    
    subgraph "Development Services"
        D[MailHog SMTP<br/>Port 1025]
        E[MailHog Web UI<br/>Port 8025]
    end
    
    subgraph "External Dependencies"
        F[Email Templates]
        G[JWT Secret]
        H[CORS Configuration]
    end
    
    B --> A
    A --> C
    A --> D
    A --> F
    A --> G
    A --> H
    
    D --> E
    
    style A fill:#f3e5f5
    style B fill:#e1f5fe
    style C fill:#e3f2fd
    style D fill:#fff8e1
    style E fill:#fff8e1
    style F fill:#f1f8e9
    style G fill:#f1f8e9
    style H fill:#f1f8e9
```

## Key Components Summary

### Frontend Services
- **Authentication Pages**: Login, Signup, Verify, Reset
- **Protected Routes**: Dashboard, Builder
- **Token Management**: JWT storage and validation
- **API Integration**: RESTful API calls to backend

### Backend Services
- **Auth Router**: All authentication endpoints
- **Security Utils**: Password hashing, JWT handling
- **Email Service**: SMTP integration with MailHog
- **Database Service**: User and token management
- **Audit Service**: Comprehensive logging

### Database Schema
- **User Table**: Core user information
- **Token Tables**: Email verification and password reset
- **Audit Table**: Security event logging
- **Organization Table**: Multi-tenant support

### External Services
- **MailHog**: Development email server
- **SQL Server**: Primary database
- **JWT**: Token-based authentication
- **CORS**: Cross-origin resource sharing

This architecture provides a complete, secure, and scalable authentication system ready for UAT testing.
