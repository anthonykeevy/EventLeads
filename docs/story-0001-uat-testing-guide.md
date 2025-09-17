# Story 0001 UAT Testing Guide - Auth & Org Foundation

## 🎯 UAT Objective
Complete User Acceptance Testing for the authentication and organization foundation system to verify all acceptance criteria are met and the system is ready for production.

## 📋 Pre-UAT Checklist

### Environment Setup
- [ ] **Application Running**: All services started via `.\scripts\start-dev.ps1`
- [ ] **Database Connected**: SQL Server with Windows Authentication
- [ ] **MailHog Active**: Email testing service running on port 8025
- [ ] **Test Users Created**: Provisioned via `python backend/scripts/provision_roles_users.py`

### Access Points Verified
- [ ] **Frontend**: http://localhost:3000 (Next.js)
- [ ] **Backend API**: http://localhost:8000 (FastAPI)
- [ ] **API Documentation**: http://localhost:8000/docs (Swagger UI)
- [ ] **MailHog Web UI**: http://localhost:8025 (Email testing)

## 🧪 UAT Test Scenarios

### Test Credentials
| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| SystemAdmin | sysadmin@local.dev | TestPassword123! | Full platform access |
| Admin | admin@local.dev | TestPassword123! | Organization admin |
| User | user@local.dev | TestPassword123! | Standard user |

---

## 📝 UAT Test Execution

### **Test 1: User Registration Flow**

#### 1.1 New User Signup
**Objective**: Verify new user can register and receive email verification

**Steps**:
1. Navigate to http://localhost:3000
2. Click "Sign up" or navigate to `/signup`
3. Fill in registration form:
   - Email: `newuser@test.com`
   - Password: `TestPassword123!`
4. Click "Create account"
5. Verify success message: "Verification required. Check your email."

**Expected Results**:
- ✅ User account created in database
- ✅ Verification email sent to MailHog
- ✅ User redirected to success page
- ✅ User cannot login until verified

**MailHog Verification**:
1. Open http://localhost:8025
2. Check for verification email to `newuser@test.com`
3. Verify email contains verification link
4. Click verification link

**Expected Results**:
- ✅ Email verification page loads
- ✅ Success message: "Email verified. You may now login."
- ✅ User can now login with credentials

#### 1.2 Duplicate Email Registration
**Objective**: Verify system prevents duplicate email registration

**Steps**:
1. Try to register with existing email: `user@local.dev`
2. Submit registration form

**Expected Results**:
- ✅ Error message: "Account already exists"
- ✅ No duplicate user created

---

### **Test 2: User Authentication Flow**

#### 2.1 Successful Login
**Objective**: Verify authenticated users can login and access protected routes

**Steps**:
1. Navigate to http://localhost:3000/login
2. Login with test credentials:
   - Email: `user@local.dev`
   - Password: `TestPassword123!`
3. Click "Login"

**Expected Results**:
- ✅ Successful login
- ✅ Redirected to dashboard
- ✅ JWT token stored in browser
- ✅ User profile displayed

#### 2.2 Unverified User Login
**Objective**: Verify unverified users cannot login

**Steps**:
1. Create unverified user (from Test 1.1)
2. Try to login with unverified credentials

**Expected Results**:
- ✅ Error message: "Email not verified"
- ✅ User remains on login page
- ✅ No JWT token issued

#### 2.3 Invalid Credentials
**Objective**: Verify system rejects invalid credentials

**Steps**:
1. Try to login with:
   - Email: `user@local.dev`
   - Password: `WrongPassword123!`

**Expected Results**:
- ✅ Error message: "Invalid credentials"
- ✅ User remains on login page
- ✅ No JWT token issued

#### 2.4 Non-existent User
**Objective**: Verify system handles non-existent users

**Steps**:
1. Try to login with:
   - Email: `nonexistent@test.com`
   - Password: `TestPassword123!`

**Expected Results**:
- ✅ Error message: "Invalid credentials"
- ✅ User remains on login page

---

### **Test 3: Protected Route Access**

#### 3.1 Authenticated Access
**Objective**: Verify authenticated users can access protected routes

**Steps**:
1. Login with valid credentials
2. Navigate to protected routes:
   - Dashboard: http://localhost:3000/
   - Builder: http://localhost:3000/builder/1
   - Events: http://localhost:3000/events

**Expected Results**:
- ✅ All protected routes accessible
- ✅ User profile information displayed
- ✅ No redirect to login page

#### 3.2 Unauthenticated Access
**Objective**: Verify unauthenticated users are redirected to login

**Steps**:
1. Clear browser storage (localStorage)
2. Navigate to protected routes:
   - Dashboard: http://localhost:3000/
   - Builder: http://localhost:3000/builder/1

**Expected Results**:
- ✅ Automatic redirect to login page
- ✅ Protected content not accessible
- ✅ User must authenticate first

#### 3.3 Role-Based Access
**Objective**: Verify role-based access control works

**Steps**:
1. Login as different role users:
   - SystemAdmin: `sysadmin@local.dev`
   - Admin: `admin@local.dev`
   - User: `user@local.dev`
2. Check `/auth/me` endpoint for role information

**Expected Results**:
- ✅ Each user sees correct role
- ✅ Role information displayed in profile
- ✅ JWT token contains role claim

---

### **Test 4: Password Reset Flow**

#### 4.1 Password Reset Request
**Objective**: Verify users can request password reset

**Steps**:
1. Navigate to http://localhost:3000/reset/request
2. Enter email: `user@local.dev`
3. Click "Send reset link"

**Expected Results**:
- ✅ Success message: "If registered, a reset email has been sent."
- ✅ Reset email sent to MailHog
- ✅ Reset token created in database

**MailHog Verification**:
1. Check MailHog for reset email
2. Verify email contains reset link
3. Click reset link

#### 4.2 Password Reset Confirmation
**Objective**: Verify password reset completion

**Steps**:
1. From reset email, navigate to reset confirmation page
2. Enter new password: `NewPassword123!`
3. Click "Reset password"

**Expected Results**:
- ✅ Success message: "Password updated"
- ✅ User can login with new password
- ✅ Old password no longer works
- ✅ Reset token consumed (one-time use)

#### 4.3 Invalid Reset Token
**Objective**: Verify invalid reset tokens are rejected

**Steps**:
1. Try to use expired or invalid reset token
2. Attempt password reset

**Expected Results**:
- ✅ Error message: "Invalid token" or "Token expired"
- ✅ Password reset fails
- ✅ User must request new reset

---

### **Test 5: Rate Limiting**

#### 5.1 Resend Verification Rate Limit
**Objective**: Verify rate limiting on resend verification

**Steps**:
1. Create unverified user
2. Request verification email multiple times quickly
3. Check for rate limiting

**Expected Results**:
- ✅ First few requests succeed
- ✅ Rate limit triggered after 5 requests
- ✅ Error message: "Daily resend limit reached"
- ✅ 60-second cooldown enforced

#### 5.2 Password Reset Rate Limit
**Objective**: Verify rate limiting on password reset

**Steps**:
1. Request password reset multiple times quickly
2. Check for rate limiting

**Expected Results**:
- ✅ Rate limiting applied
- ✅ Abuse prevention working
- ✅ Legitimate users not affected

---

### **Test 6: API Endpoint Testing**

#### 6.1 API Documentation
**Objective**: Verify API documentation is accessible

**Steps**:
1. Navigate to http://localhost:8000/docs
2. Explore API endpoints
3. Test endpoints using Swagger UI

**Expected Results**:
- ✅ API documentation loads
- ✅ All auth endpoints documented
- ✅ Interactive testing available

#### 6.2 Direct API Testing
**Objective**: Verify API endpoints work correctly

**Steps**:
1. Test signup endpoint:
   ```bash
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"apitest@test.com","password":"TestPassword123!"}'
   ```

2. Test login endpoint:
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user@local.dev","password":"TestPassword123!"}'
   ```

**Expected Results**:
- ✅ API endpoints respond correctly
- ✅ JSON responses properly formatted
- ✅ Error handling works
- ✅ CORS headers present

---

### **Test 7: Security Features**

#### 7.1 JWT Token Security
**Objective**: Verify JWT tokens are secure

**Steps**:
1. Login and capture JWT token
2. Verify token structure and claims
3. Test token expiration

**Expected Results**:
- ✅ JWT token properly formatted
- ✅ Contains user ID, role, expiration
- ✅ Token expires after 8 hours
- ✅ Invalid tokens rejected

#### 7.2 Password Security
**Objective**: Verify password security measures

**Steps**:
1. Check database for password hashes
2. Verify passwords are hashed (not plain text)
3. Test password verification

**Expected Results**:
- ✅ Passwords stored as hashes
- ✅ Bcrypt hashing used
- ✅ Salt included in hash
- ✅ Password verification works

#### 7.3 Audit Logging
**Objective**: Verify security events are logged

**Steps**:
1. Perform various auth actions
2. Check database for audit events
3. Verify event details

**Expected Results**:
- ✅ All auth events logged
- ✅ IP address and User-Agent tracked
- ✅ Event types and status recorded
- ✅ Timestamps accurate

---

## ✅ UAT Sign-off Checklist

### Functional Requirements
- [ ] **User Registration**: New users can signup and verify email
- [ ] **User Authentication**: Login/logout works correctly
- [ ] **Password Reset**: Users can reset forgotten passwords
- [ ] **Protected Routes**: Authentication required for protected content
- [ ] **Role-Based Access**: Different user roles work correctly
- [ ] **Email Integration**: Emails sent and received via MailHog

### Security Requirements
- [ ] **Password Security**: Passwords properly hashed and secured
- [ ] **JWT Security**: Tokens secure with proper expiration
- [ ] **Rate Limiting**: Abuse prevention working
- [ ] **Audit Logging**: Security events properly logged
- [ ] **Input Validation**: Malicious inputs rejected
- [ ] **Error Handling**: Secure error messages

### Performance Requirements
- [ ] **Response Times**: API responses under 2 seconds
- [ ] **Database Performance**: Queries execute efficiently
- [ ] **Frontend Performance**: Pages load quickly
- [ ] **Email Delivery**: Emails sent within 5 seconds

### User Experience Requirements
- [ ] **Intuitive Interface**: Easy to use and navigate
- [ ] **Clear Error Messages**: Helpful feedback to users
- [ ] **Responsive Design**: Works on different screen sizes
- [ ] **Accessibility**: Basic accessibility features work

## 🚨 UAT Issues & Resolution

### Critical Issues (Must Fix)
- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]
- [ ] Issue 3: [Description]

### Minor Issues (Should Fix)
- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]

### Enhancement Requests (Could Fix)
- [ ] Enhancement 1: [Description]
- [ ] Enhancement 2: [Description]

## 📊 UAT Results Summary

### Test Results
- **Total Tests**: 25
- **Passed**: ___
- **Failed**: ___
- **Blocked**: ___
- **Pass Rate**: ___%

### Acceptance Criteria Status
- [ ] **AC1**: POST /auth/signup - User registration
- [ ] **AC2**: GET /auth/verify - Email verification
- [ ] **AC3**: POST /auth/resend - Resend verification
- [ ] **AC4**: POST /auth/login - User authentication
- [ ] **AC5**: GET /auth/me - Protected route access
- [ ] **AC6**: Route protection - JWT validation
- [ ] **AC7**: POST /auth/reset/request - Password reset request
- [ ] **AC8**: POST /auth/reset/confirm - Password reset confirmation
- [ ] **AC9**: AppShell - Protected UI components
- [ ] **AC10**: Error/State Copy - User feedback
- [ ] **AC11**: Tokens - Secure token handling
- [ ] **AC12**: Logging & Metrics - Audit logging
- [ ] **AC13**: Audit & Interaction Logging - Security events

## 🎯 UAT Sign-off

### UAT Tester
- **Name**: ________________
- **Date**: ________________
- **Signature**: ________________

### UAT Approval
- **Status**: [ ] PASSED [ ] FAILED [ ] CONDITIONAL PASS
- **Comments**: ________________
- **Next Steps**: ________________

---

**UAT Testing Guide Version**: 1.0  
**Last Updated**: January 2025  
**Story**: 0001 - Auth & Org Foundation  
**Status**: Ready for UAT Execution
