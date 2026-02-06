# MoneyMentor - Development Server Starter
# This script starts both backend and frontend servers

Write-Host "🚀 Starting MoneyMentor Development Environment..." -ForegroundColor Green
Write-Host ""

# Get the script directory
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if Node is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Checking backend dependencies..." -ForegroundColor Yellow
$backendDir = Join-Path $ROOT_DIR "backend"

if (-not (Test-Path (Join-Path $backendDir "venv"))) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv (Join-Path $backendDir "venv")
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
$activateScript = Join-Path $backendDir "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    & $activateScript
    pip install -r (Join-Path $backendDir "requirements.txt") --quiet
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Starting services..." -ForegroundColor Green
Write-Host ""

# Start Backend in new window
Write-Host "Starting Backend Server on http://localhost:8000" -ForegroundColor Cyan
$backendScript = @"
cd '$backendDir'
. .\venv\Scripts\Activate.ps1
python main.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "Starting Frontend Server on http://localhost:8080" -ForegroundColor Cyan
$frontendScript = @"
cd '$ROOT_DIR'
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=".PadRight(60, '=') -ForegroundColor Green
Write-Host ""
Write-Host "✅ MoneyMentor is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Email:    demo@moneymentor.com" -ForegroundColor White
Write-Host "  Password: demo123" -ForegroundColor White
Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=".PadRight(60, '=') -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to open the application in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "✨ MoneyMentor is ready! Happy investing! ✨" -ForegroundColor Green
Write-Host ""
