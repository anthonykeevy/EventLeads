# Story 0001 File Change Monitor
# This script monitors for changes to Story 0001 core files and alerts when regression testing may be needed

param(
    [string]$Action = "check",  # check, list, watch
    [string]$GitRef = "HEAD~1"  # Git reference to compare against
)

# Story 0001 Core Files to Monitor
$Story0001Files = @(
    # Backend Core Files
    "backend/app/routers/auth.py",
    "backend/app/models/user.py", 
    "backend/app/models/emailverificationtoken.py",
    "backend/app/models/passwordresettoken.py",
    "backend/app/models/authevent.py",
    "backend/app/utils/security.py",
    "backend/app/schemas/auth.py",
    "backend/app/core/settings.py",
    
    # Frontend Core Files
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/login/page.tsx",
    "frontend/src/app/verify/page.tsx",
    "frontend/src/app/resend/page.tsx",
    "frontend/src/app/reset/request/page.tsx",
    "frontend/src/app/reset/confirm/page.tsx",
    "frontend/src/lib/auth.ts",
    "frontend/src/lib/api.ts",
    
    # Configuration Files
    ".env.dev",
    "docs/shards/02-data-schema.md",
    
    # Database Migrations
    "backend/migrations/versions/a013_*.py",
    
    # Documentation Files
    "docs/stories/0001-auth-org-foundation.md",
    "docs/story-0001-uat-signoff-checklist.md",
    "docs/story-0001-implementation-walkthrough.md"
)

function Show-Header {
    Write-Host "Story 0001 File Change Monitor" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
}

function Get-ChangedFiles {
    param([string]$Ref)
    
    try {
        # Always check all files in the current commit for Story 0001 monitoring
        # This approach works for both first commit and subsequent commits
        Write-Host "Checking all files in current commit for Story 0001 changes" -ForegroundColor Gray
        $allFiles = git ls-tree -r --name-only HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $allFiles
        } else {
            Write-Warning "Git ls-tree command failed."
            return @()
        }
    } catch {
        Write-Warning "Error checking git changes: $_"
        return @()
    }
}

function Test-Story0001File {
    param([string]$FilePath)
    
    foreach ($storyFile in $Story0001Files) {
        if ($FilePath -like $storyFile -or $FilePath -match [regex]::Escape($storyFile)) {
            return $true
        }
    }
    return $false
}

function Show-Story0001Files {
    Write-Host "Story 0001 Core Files:" -ForegroundColor Yellow
    Write-Host ""
    
    $categories = @{
        "Backend Core" = @()
        "Frontend Core" = @()
        "Configuration" = @()
        "Database" = @()
        "Documentation" = @()
    }
    
    foreach ($file in $Story0001Files) {
        if ($file -like "backend/app/*") {
            $categories["Backend Core"] += $file
        } elseif ($file -like "frontend/src/*") {
            $categories["Frontend Core"] += $file
        } elseif ($file -like ".env*" -or $file -like "docs/shards/*") {
            $categories["Configuration"] += $file
        } elseif ($file -like "*migrations*") {
            $categories["Database"] += $file
        } else {
            $categories["Documentation"] += $file
        }
    }
    
    foreach ($category in $categories.Keys) {
        if ($categories[$category].Count -gt 0) {
            Write-Host "  $category" -ForegroundColor Green
            foreach ($file in $categories[$category]) {
                Write-Host "    • $file" -ForegroundColor White
            }
            Write-Host ""
        }
    }
}

function Check-ForChanges {
    param([string]$Ref)
    
    Write-Host "Checking for changes since $Ref..." -ForegroundColor Yellow
    Write-Host ""
    
    $changedFiles = Get-ChangedFiles -Ref $Ref
    $story0001Changes = @()
    
    foreach ($file in $changedFiles) {
        if (Test-Story0001File -FilePath $file) {
            $story0001Changes += $file
        }
    }
    
    if ($story0001Changes.Count -eq 0) {
        Write-Host "SUCCESS: No Story 0001 files have been modified since $Ref" -ForegroundColor Green
        Write-Host ""
        return
    }
    
    Write-Host "WARNING: Story 0001 files have been modified!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Modified Files:" -ForegroundColor Yellow
    foreach ($file in $story0001Changes) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "RECOMMENDED ACTIONS:" -ForegroundColor Cyan
    Write-Host "  1. Run UAT Testing: docs/story-0001-uat-signoff-checklist.md" -ForegroundColor White
    Write-Host "  2. Test Auth Flows: Signup -> Verify -> Login -> Reset" -ForegroundColor White
    Write-Host "  3. Verify Rate Limiting: Test resend and reset limits" -ForegroundColor White
    Write-Host "  4. Check Security: Verify JWT, tokens, and audit logging" -ForegroundColor White
    Write-Host "  5. Update Documentation: Reflect any changes made" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Quick Test Commands:" -ForegroundColor Cyan
    Write-Host "  .\scripts\story-0001-uat-helper.ps1 -Action status" -ForegroundColor White
    Write-Host "  .\scripts\story-0001-uat-helper.ps1 -Action api" -ForegroundColor White
    Write-Host ""
}

function Watch-ForChanges {
    Write-Host "Watching for Story 0001 file changes..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop watching" -ForegroundColor Gray
    Write-Host ""
    
    $lastCommit = git rev-parse HEAD
    
    while ($true) {
        Start-Sleep -Seconds 5
        
        $currentCommit = git rev-parse HEAD
        if ($currentCommit -ne $lastCommit) {
            Write-Host "New commit detected: $currentCommit" -ForegroundColor Cyan
            Check-ForChanges -Ref $lastCommit
            $lastCommit = $currentCommit
        }
    }
}

function Show-Help {
    Write-Host "Story 0001 File Change Monitor" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\monitor-story-0001-changes.ps1 [Action] [GitRef]" -ForegroundColor White
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  check  - Check for changes since specified git reference (default: HEAD~1)" -ForegroundColor White
    Write-Host "  list   - List all Story 0001 core files" -ForegroundColor White
    Write-Host "  watch  - Continuously watch for changes (requires git repository)" -ForegroundColor White
    Write-Host "  help   - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\monitor-story-0001-changes.ps1 check" -ForegroundColor White
    Write-Host "  .\scripts\monitor-story-0001-changes.ps1 check HEAD~5" -ForegroundColor White
    Write-Host "  .\scripts\monitor-story-0001-changes.ps1 list" -ForegroundColor White
    Write-Host "  .\scripts\monitor-story-0001-changes.ps1 watch" -ForegroundColor White
    Write-Host ""
}

# Main execution
Show-Header

switch ($Action.ToLower()) {
    "check" {
        Check-ForChanges -Ref $GitRef
    }
    "list" {
        Show-Story0001Files
    }
    "watch" {
        Watch-ForChanges
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "ERROR: Unknown action: $Action" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}

Write-Host ""
Write-Host "For more information, see: docs/story-0001-signoff-complete.md" -ForegroundColor Cyan
