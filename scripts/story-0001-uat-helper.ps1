# Story 0001 UAT Testing Helper Script
# This script helps automate UAT testing tasks for Story 0001: Auth & Org Foundation

param(
    [string]$Action = "help"
)

function Show-UATStatus {
    Write-Host "=== Story 0001 UAT Testing Status ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if services are running
    Write-Host "Checking services..." -ForegroundColor Yellow
    
    $services = @(
        @{Name="Frontend"; Port=3000; URL="http://localhost:3000"},
        @{Name="Backend API"; Port=8000; URL="http://localhost:8000"},
        @{Name="MailHog Web"; Port=8025; URL="http://localhost:8025"},
        @{Name="MailHog SMTP"; Port=1025; URL="localhost:1025"}
    )
    
    foreach ($service in $services) {
        $connection = Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($connection) {
            Write-Host "✅ $($service.Name) - Running on port $($service.Port)" -ForegroundColor Green
        } else {
            Write-Host "❌ $($service.Name) - Not running on port $($service.Port)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  MailHog: http://localhost:8025" -ForegroundColor White
}

function Show-TestCredentials {
    Write-Host "=== Story 0001 UAT Test Credentials ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "SystemAdmin:" -ForegroundColor Yellow
    Write-Host "  Email: sysadmin@local.dev" -ForegroundColor White
    Write-Host "  Password: TestPassword123!" -ForegroundColor White
    Write-Host ""
    Write-Host "Admin:" -ForegroundColor Yellow
    Write-Host "  Email: admin@local.dev" -ForegroundColor White
    Write-Host "  Password: TestPassword123!" -ForegroundColor White
    Write-Host ""
    Write-Host "User:" -ForegroundColor Yellow
    Write-Host "  Email: user@local.dev" -ForegroundColor White
    Write-Host "  Password: TestPassword123!" -ForegroundColor White
    Write-Host ""
}

function Test-APIEndpoints {
    Write-Host "=== API Endpoint Testing ===" -ForegroundColor Cyan
    Write-Host ""
    
    $baseUrl = "http://localhost:8000"
    
    # Test health endpoint
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/healthz" -Method GET
        Write-Host "✅ Health Check - $($response.status)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Health Check - Failed" -ForegroundColor Red
    }
    
    # Test ready endpoint
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/readyz" -Method GET
        Write-Host "✅ Readiness Check - $($response.ready)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Readiness Check - Failed" -ForegroundColor Red
    }
    
    # Test API docs
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method GET
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API Documentation - Accessible" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ API Documentation - Not accessible" -ForegroundColor Red
    }
}

function Test-Login {
    param([string]$Email, [string]$Password)
    
    Write-Host "=== Testing Login ===" -ForegroundColor Cyan
    Write-Host "Email: $Email" -ForegroundColor Yellow
    
    $loginData = @{
        email = $Email
        password = $Password
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $loginData -ContentType "application/json"
        Write-Host "✅ Login Successful - Token received" -ForegroundColor Green
        return $response.access_token
    } catch {
        Write-Host "❌ Login Failed - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Test-ProtectedRoute {
    param([string]$Token)
    
    if (-not $Token) {
        Write-Host "❌ No token provided for protected route test" -ForegroundColor Red
        return
    }
    
    Write-Host "=== Testing Protected Route ===" -ForegroundColor Cyan
    
    $headers = @{
        Authorization = "Bearer $Token"
    }
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/auth/me" -Method GET -Headers $headers
        Write-Host "✅ Protected Route Access - User ID: $($response.user_id), Role: $($response.role)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Protected Route Access - Failed" -ForegroundColor Red
    }
}

function Show-UATSteps {
    Write-Host "=== Story 0001 UAT Testing Steps ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Start Application:" -ForegroundColor Yellow
    Write-Host "   .\scripts\start-dev.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Check Services:" -ForegroundColor Yellow
    Write-Host "   .\scripts\story-0001-uat-helper.ps1 -Action status" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Test API Endpoints:" -ForegroundColor Yellow
    Write-Host "   .\scripts\story-0001-uat-helper.ps1 -Action api" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Test Login:" -ForegroundColor Yellow
    Write-Host "   .\scripts\story-0001-uat-helper.ps1 -Action login" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Manual Testing:" -ForegroundColor Yellow
    Write-Host "   - Open http://localhost:3000" -ForegroundColor White
    Write-Host "   - Test signup, login, password reset" -ForegroundColor White
    Write-Host "   - Check MailHog at http://localhost:8025" -ForegroundColor White
    Write-Host ""
    Write-Host "6. Review UAT Guide:" -ForegroundColor Yellow
    Write-Host "   docs/story-0001-uat-testing-guide.md" -ForegroundColor White
}

function Show-Help {
    Write-Host "=== Story 0001 UAT Testing Helper ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\story-0001-uat-helper.ps1 -Action [action]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  status    - Check if all services are running" -ForegroundColor White
    Write-Host "  credentials - Show test credentials" -ForegroundColor White
    Write-Host "  api       - Test API endpoints" -ForegroundColor White
    Write-Host "  login     - Test login functionality" -ForegroundColor White
    Write-Host "  steps     - Show UAT testing steps" -ForegroundColor White
    Write-Host "  help      - Show this help message" -ForegroundColor White
    Write-Host ""
}

# Main script logic
switch ($Action.ToLower()) {
    "status" {
        Show-UATStatus
    }
    "credentials" {
        Show-TestCredentials
    }
    "api" {
        Test-APIEndpoints
    }
    "login" {
        $token = Test-Login -Email "user@local.dev" -Password "TestPassword123!"
        if ($token) {
            Test-ProtectedRoute -Token $token
        }
    }
    "steps" {
        Show-UATSteps
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
}
