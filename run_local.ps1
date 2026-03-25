# PowerShell script for running Omon Logistics API locally

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Omon Logistics - Local Development Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.12 from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Run migrations
Write-Host ""
Write-Host "Applying database migrations..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to apply migrations" -ForegroundColor Red
    exit 1
}

# Create migrations
Write-Host ""
Write-Host "Creating new migrations..." -ForegroundColor Yellow
python manage.py makemigrations
if ($LASTEXITCODE -eq 0) {
    # Apply new migrations if any were created
    Write-Host "Applying new migrations..." -ForegroundColor Yellow
    python manage.py migrate
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to apply new migrations" -ForegroundColor Red
        exit 1
    }
}

# Start development server
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Starting Django Development Server" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/api/docs/" -ForegroundColor Green
Write-Host "Admin Panel: http://localhost:8000/admin/" -ForegroundColor Green
Write-Host "API Root: http://localhost:8000/api/" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 0.0.0.0:8000

