@echo off
REM ============================================
REM SPAS - Database Initialization Script (Windows)
REM ============================================
REM This script initializes the PostgreSQL database for SPAS
REM Usage: scripts\init_db.bat

setlocal enabledelayedexpansion

echo ========================================
echo SPAS Database Initialization
echo ========================================

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo [INFO] Copy .env.example to .env and configure it
    exit /b 1
)

REM Load environment variables from .env
for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
    )
)

REM Set default values if not configured
if "%DB_NAME%"=="" set DB_NAME=spas_db
if "%DB_USER%"=="" set DB_USER=spas_user
if "%DB_PASSWORD%"=="" set DB_PASSWORD=your_password
if "%DB_HOST%"=="" set DB_HOST=localhost
if "%DB_PORT%"=="" set DB_PORT=5432

echo.
echo Database Configuration:
echo   Name: %DB_NAME%
echo   User: %DB_USER%
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PostgreSQL is not installed or not in PATH
    echo [INFO] Install PostgreSQL and add it to your PATH
    echo [INFO] Download from: https://www.postgresql.org/download/windows/
    exit /b 1
)

echo.
echo [INFO] Checking PostgreSQL service...
sc query postgresql-x64-14 | find "RUNNING" >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL service may not be running
    echo [INFO] Starting PostgreSQL service...
    net start postgresql-x64-14 2>nul
    if %errorlevel% neq 0 (
        echo [WARNING] Could not start PostgreSQL service automatically
        echo [INFO] Please start it manually from Services
        pause
    )
)
echo [OK] PostgreSQL service is running

REM Create database user (if not exists)
echo.
echo [INFO] Creating database user...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -tc "SELECT 1 FROM pg_user WHERE usename = '%DB_USER%'" | findstr /C:"1" >nul
if %errorlevel% neq 0 (
    psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create database user
        exit /b 1
    )
    echo [OK] Database user created
) else (
    echo [OK] Database user already exists
)

REM Create database (if not exists)
echo.
echo [INFO] Creating database...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -lqt | findstr /C:"%DB_NAME%" >nul
if %errorlevel% neq 0 (
    psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create database
        exit /b 1
    )
    echo [OK] Database created
) else (
    echo [OK] Database already exists
)

REM Grant privileges
echo.
echo [INFO] Granting privileges...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
psql -U postgres -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "GRANT ALL ON SCHEMA public TO %DB_USER%;"
echo [OK] Privileges granted

REM Install required extensions
echo.
echo [INFO] Installing PostgreSQL extensions...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
echo [OK] Extensions installed

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo.
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run Django migrations
echo.
echo [INFO] Running Django migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create migrations
    exit /b 1
)

python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to apply migrations
    exit /b 1
)
echo [OK] Migrations completed

REM Create superuser
echo.
echo [INFO] Creating superuser...
echo [INFO] You will be prompted to create an admin user
python manage.py createsuperuser --username admin --email admin@spas.local
if %errorlevel% neq 0 (
    echo [WARNING] Superuser creation failed or was skipped
)

REM Load initial data (if fixtures exist)
echo.
echo [INFO] Loading initial data...
if exist fixtures (
    python manage.py loaddata fixtures\*.json 2>nul
    if %errorlevel% neq 0 (
        echo [INFO] No fixtures found or error loading fixtures
    )
) else (
    echo [INFO] No fixtures directory found
)

echo.
echo ========================================
echo [SUCCESS] Database initialization completed!
echo ========================================
echo.
echo Next steps:
echo   1. Start the development server: python manage.py runserver
echo   2. Access admin panel: http://localhost:8000/admin
echo   3. Login with the admin credentials you just created
echo.
pause
