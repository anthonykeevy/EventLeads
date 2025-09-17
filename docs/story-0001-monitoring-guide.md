# Story 0001 File Change Monitoring Guide

## 📋 **Overview**

This guide explains how to use the Story 0001 file change monitoring system to ensure that any modifications to the authentication system are properly tested and validated.

## 🎯 **Purpose**

The monitoring system helps you:
- **Detect Changes**: Automatically identify when Story 0001 core files are modified
- **Prevent Regressions**: Ensure authentication system remains functional after changes
- **Maintain Quality**: Enforce proper testing before deployment
- **Track Impact**: Understand what changes affect the auth system

---

## 📁 **Story 0001 Core Files**

### **Backend Core Files**
```
backend/app/routers/auth.py                    # Core auth endpoints
backend/app/models/user.py                     # User model
backend/app/models/emailverificationtoken.py   # Email verification
backend/app/models/passwordresettoken.py       # Password reset
backend/app/models/authevent.py                # Audit logging
backend/app/utils/security.py                  # Security utilities
backend/app/schemas/auth.py                    # API schemas
backend/app/core/settings.py                   # Application settings
```

### **Frontend Core Files**
```
frontend/src/app/signup/page.tsx               # Signup page
frontend/src/app/login/page.tsx                # Login page
frontend/src/app/verify/page.tsx               # Email verification
frontend/src/app/resend/page.tsx               # Resend verification
frontend/src/app/reset/request/page.tsx        # Reset request
frontend/src/app/reset/confirm/page.tsx        # Reset confirmation
frontend/src/lib/auth.ts                       # Auth utilities
frontend/src/lib/api.ts                        # API client
```

### **Configuration Files**
```
.env.dev                                       # Environment variables
docs/shards/02-data-schema.md                 # Database standards
```

### **Database Migrations**
```
backend/migrations/versions/a013_*.py          # Story 0001 migrations
```

### **Documentation Files**
```
docs/stories/0001-auth-org-foundation.md      # Main story
docs/story-0001-uat-signoff-checklist.md      # UAT checklist
docs/story-0001-implementation-walkthrough.md # Implementation guide
docs/story-0001-signoff-complete.md           # Signoff document
```

---

## 🔧 **Monitoring Methods**

### **1. Manual PowerShell Script** (Recommended for Local Development)

#### **Script Location**
```
scripts/monitor-story-0001-changes.ps1
```

#### **Usage Commands**

**Check for changes since last commit:**
```powershell
.\scripts\monitor-story-0001-changes.ps1 check
```

**Check for changes since specific commit:**
```powershell
.\scripts\monitor-story-0001-changes.ps1 check HEAD~5
```

**List all Story 0001 core files:**
```powershell
.\scripts\monitor-story-0001-changes.ps1 list
```

**Watch for changes in real-time:**
```powershell
.\scripts\monitor-story-0001-changes.ps1 watch
```

**Show help:**
```powershell
.\scripts\monitor-story-0001-changes.ps1 help
```

#### **Example Output**
```
Story 0001 File Change Monitor
=================================

Checking for changes since HEAD~1...

WARNING: Story 0001 files have been modified!

Modified Files:
  - backend/app/routers/auth.py
  - frontend/src/app/login/page.tsx

RECOMMENDED ACTIONS:
  1. Run UAT Testing: docs/story-0001-uat-signoff-checklist.md
  2. Test Auth Flows: Signup -> Verify -> Login -> Reset
  3. Verify Rate Limiting: Test resend and reset limits
  4. Check Security: Verify JWT, tokens, and audit logging
  5. Update Documentation: Reflect any changes made

Quick Test Commands:
  .\scripts\story-0001-uat-helper.ps1 -Action status
  .\scripts\story-0001-uat-helper.ps1 -Action api
```

### **2. GitHub Actions** (Automated for CI/CD)

#### **Workflow Location**
```
.github/workflows/story-0001-monitor.yml
```

#### **Automatic Triggers**
- **Pull Requests**: Comments on PRs that modify Story 0001 files
- **Main/Develop Branch**: Creates issues when files are modified

#### **What It Does**
1. **Detects Changes**: Scans for modifications to Story 0001 files
2. **PR Comments**: Adds warning comments with testing recommendations
3. **Issue Creation**: Creates tracking issues for branch changes
4. **Documentation Links**: Provides links to UAT checklist and guides

#### **Example PR Comment**
```markdown
## 🚨 Story 0001 Files Modified

**Warning**: This PR modifies files that are part of Story 0001 (Auth & Org Foundation). Regression testing is recommended.

### Modified Files:
- `backend/app/routers/auth.py`
- `frontend/src/app/login/page.tsx`

### 📋 Recommended Actions:
1. **Run UAT Testing**: Review [UAT Checklist](docs/story-0001-uat-signoff-checklist.md)
2. **Test Auth Flows**: Signup → Verify → Login → Reset
3. **Verify Rate Limiting**: Test resend and reset limits
4. **Check Security**: Verify JWT, tokens, and audit logging
5. **Update Documentation**: Reflect any changes made

### 🧪 Quick Test Commands:
```bash
# Check service status
.\scripts\story-0001-uat-helper.ps1 -Action status

# Test API endpoints
.\scripts\story-0001-uat-helper.ps1 -Action api
```

### 📚 Documentation:
- [Story 0001 Signoff](docs/story-0001-signoff-complete.md)
- [Implementation Guide](docs/story-0001-implementation-walkthrough.md)
- [UAT Checklist](docs/story-0001-uat-signoff-checklist.md)
```

### **3. Git Hooks** (Optional - Advanced)

#### **Pre-commit Hook**
```bash
#!/bin/bash
# .git/hooks/pre-commit

STORY_0001_FILES=(
    "backend/app/routers/auth.py"
    "backend/app/models/user.py"
    "frontend/src/app/signup/page.tsx"
    # ... other files
)

for file in "${STORY_0001_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "$file"; then
        echo "⚠️  WARNING: Story 0001 file modified: $file"
        echo "📋 Consider running regression testing for Story 0001"
        echo "🧪 UAT checklist: docs/story-0001-uat-signoff-checklist.md"
    fi
done
```

---

## 🧪 **When Changes Are Detected**

### **Immediate Actions Required**

1. **Run UAT Testing**
   - Use: `docs/story-0001-uat-signoff-checklist.md`
   - Test all authentication flows
   - Verify rate limiting functionality
   - Check security features

2. **Test Auth Flows**
   - **Signup Flow**: Registration → Email verification → Login
   - **Login Flow**: Authentication → Protected route access
   - **Reset Flow**: Request → Email → Token → New password
   - **Rate Limiting**: Test resend and reset limits

3. **Verify Security**
   - JWT token validation
   - Password hashing
   - Token expiration
   - Audit logging

4. **Update Documentation**
   - Reflect any changes made
   - Update implementation notes
   - Revise UAT checklist if needed

### **Quick Test Commands**

**Check service status:**
```powershell
.\scripts\story-0001-uat-helper.ps1 -Action status
```

**Test API endpoints:**
```powershell
.\scripts\story-0001-uat-helper.ps1 -Action api
```

**Test login flow:**
```powershell
.\scripts\story-0001-uat-helper.ps1 -Action login
```

---

## 📊 **Monitoring Best Practices**

### **Daily Development**
1. **Before Committing**: Run `.\scripts\monitor-story-0001-changes.ps1 check`
2. **After Pulling**: Check for changes that might affect auth system
3. **Before Testing**: Verify no unexpected changes to core files

### **Release Preparation**
1. **Full Regression Test**: Run complete UAT checklist
2. **Security Review**: Verify all security features still work
3. **Documentation Update**: Ensure all changes are documented

### **Team Collaboration**
1. **PR Reviews**: Check for Story 0001 file modifications
2. **Code Reviews**: Pay special attention to auth-related changes
3. **Testing Coordination**: Ensure regression testing is performed

---

## 🚨 **Emergency Procedures**

### **If Authentication System Breaks**

1. **Immediate Assessment**
   - Check recent commits for Story 0001 file changes
   - Identify which changes caused the issue
   - Assess impact on user authentication

2. **Quick Fixes**
   - Revert problematic changes if possible
   - Deploy hotfix for critical issues
   - Communicate with team about the issue

3. **Full Recovery**
   - Run complete UAT testing
   - Verify all auth flows work correctly
   - Update monitoring system if needed

### **If Monitoring System Fails**

1. **Manual Check**
   - Review recent git history
   - Check for Story 0001 file modifications
   - Run UAT testing manually

2. **System Recovery**
   - Fix monitoring script issues
   - Update GitHub Actions workflow
   - Test monitoring system functionality

---

## 📚 **Related Documentation**

### **Primary Documents**
- **`docs/story-0001-signoff-complete.md`** - Official signoff and monitoring setup
- **`docs/story-0001-uat-signoff-checklist.md`** - UAT testing checklist
- **`docs/story-0001-implementation-walkthrough.md`** - Implementation details

### **Supporting Documents**
- **`docs/stories/0001-auth-org-foundation.md`** - Main story definition
- **`docs/shards/02-data-schema.md`** - Database standards
- **`.github/workflows/story-0001-monitor.yml`** - Automated monitoring

### **Scripts and Tools**
- **`scripts/monitor-story-0001-changes.ps1`** - Manual monitoring script
- **`scripts/story-0001-uat-helper.ps1`** - UAT testing helper

---

## 🎯 **Summary**

The Story 0001 monitoring system provides three levels of protection:

1. **Manual Monitoring**: PowerShell script for local development
2. **Automated Monitoring**: GitHub Actions for CI/CD
3. **Documentation**: Comprehensive guides and checklists

**Key Benefits:**
- ✅ **Prevents Regressions**: Catches changes before they cause issues
- ✅ **Ensures Quality**: Enforces proper testing procedures
- ✅ **Maintains Security**: Protects authentication system integrity
- ✅ **Saves Time**: Automated detection and guidance

**Remember**: Any change to Story 0001 files requires regression testing to ensure the authentication system continues to work correctly!

---

*This monitoring guide is part of the Story 0001 signoff documentation and should be referenced whenever working with the authentication system.*
