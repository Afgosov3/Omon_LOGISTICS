@echo off
REM Running Omon Logistics API locally

cd /d %~dp0

REM Check if venv exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        echo Make sure Python 3.12 is installed
        pause
        exit /b 1
    )
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Applying database migrations...
python manage.py migrate
if errorlevel 1 (
    echo Error: Failed to apply migrations
    pause
    exit /b 1
)

echo.
echo Creating makemigrations...
python manage.py makemigrations
if errorlevel 1 (
    echo Warning: Some apps might not have changes
)

echo.
echo Applying new migrations...
python manage.py migrate
if errorlevel 1 (
    echo Error: Failed to apply migrations
    pause
    exit /b 1
)

echo.
echo.
echo ============================================
echo Starting Django Development Server
echo ============================================
echo API Documentation: http://localhost:8888/api/docs/
echo Admin Panel: http://localhost:8888/admin/
echo API Root: http://localhost:8888/api/
echo ============================================
echo.

REM Server ishga tushalish
python manage.py runserver 0.0.0.0:8888
