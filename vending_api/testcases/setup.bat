@echo off
REM Urban Harvest Vending Machine API Setup Script
REM This script sets up the development environment for the FastAPI service

echo ========================================
echo Urban Harvest Vending Machine API Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Step 5: Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo Environment file created from template.
    echo IMPORTANT: Please edit .env file with your database credentials!
) else (
    echo Environment file already exists.
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your database credentials
echo 2. Create PostgreSQL database: createdb uharvest_vending
echo 3. Import schema: psql -d uharvest_vending -f ..\database\schema.sql
echo 4. Start server: python run_server.py --reload --debug
echo.
echo API will be available at:
echo - Base URL: http://localhost:8000
echo - Documentation: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/api/v1/health
echo.
echo Press any key to exit...
pause >nul
