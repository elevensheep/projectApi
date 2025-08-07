# Project Startup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Project Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Port check function
function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

# Check ports
Write-Host "Checking port status..." -ForegroundColor Yellow
$ports = @(8080, 3000, 8000)
foreach ($port in $ports) {
    if (Test-Port -Port $port) {
        Write-Host "Port $port is already in use. Please close other processes." -ForegroundColor Red
        Read-Host "Press Enter to continue"
        exit 1
    }
}

Write-Host "All ports are available." -ForegroundColor Green
Write-Host ""

# Check required programs
Write-Host "Checking required programs..." -ForegroundColor Yellow

# Check Java
try {
    $javaVersion = java -version 2>&1
    Write-Host "Java check completed" -ForegroundColor Green
}
catch {
    Write-Host "Java is not installed. Please install Java 17 or higher." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js check completed" -ForegroundColor Green
}
catch {
    Write-Host "Node.js is not installed. Please install Node.js." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "Python check completed" -ForegroundColor Green
}
catch {
    Write-Host "Python is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "All required programs are installed." -ForegroundColor Green
Write-Host ""

# Save current directory
$originalDir = Get-Location

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Start FastAPI server
Write-Host "[1/3] Starting FastAPI server... (Port: 8000)" -ForegroundColor Yellow
Set-Location "$originalDir\py"

# Check and create virtual environment
if (-not (Test-Path "venv39\Scripts\Activate.ps1")) {
    Write-Host "Python virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv39
}

# Activate virtual environment and install dependencies
& "venv39\Scripts\Activate.ps1"
pip install -r requirements.txt | Out-Null

# Start FastAPI server in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$originalDir\py'; & 'venv39\Scripts\Activate.ps1'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
Start-Sleep -Seconds 3

# 2. Start Spring Boot server
Write-Host "[2/3] Starting Spring Boot server... (Port: 8080)" -ForegroundColor Yellow
Set-Location "$originalDir\bookSpring"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$originalDir\bookSpring'; .\gradlew bootRun" -WindowStyle Normal
Start-Sleep -Seconds 5

# 3. Start React development server
Write-Host "[3/3] Starting React development server... (Port: 3000)" -ForegroundColor Yellow
Set-Location "$originalDir\frontend"

# Check and install node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install | Out-Null
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$originalDir\frontend'; npm start" -WindowStyle Normal
Start-Sleep -Seconds 3

# Return to original directory
Set-Location $originalDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   All services have been started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor White
Write-Host "- React Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "- Spring Boot API: http://localhost:8080" -ForegroundColor Cyan
Write-Host "- FastAPI: http://localhost:8000" -ForegroundColor Cyan
Write-Host "- FastAPI Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "All servers are running in background." -ForegroundColor Yellow
Write-Host "To stop servers, close each terminal window or press Ctrl+C." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue" 