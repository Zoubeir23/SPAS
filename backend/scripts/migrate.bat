@echo off
REM ============================================
REM SPAS - Complete Migration Script (Windows)
REM ============================================
REM This script handles all migration tasks for SPAS
REM Usage: scripts\migrate.bat [--fresh]

setlocal enabledelayedexpansion

echo ========================================
echo SPAS Migration Script
echo ========================================

REM Change to backend directory
cd /d %~dp0..

REM Check if fresh migration is requested
set FRESH_MIGRATION=false
if "%1"=="--fresh" set FRESH_MIGRATION=true
if "%FRESH_MIGRATION%"=="true" echo [INFO] Fresh migration requested

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

echo [OK] Environment variables loaded

REM Check migration dependencies
echo.
echo [INFO] Checking migration dependencies...

REM Create migrations directories if they don't exist
for /d %%d in (apps\*) do (
    if not exist "%%d\migrations" (
        echo [INFO] Creating migrations directory for %%d
        mkdir "%%d\migrations"
        type nul > "%%d\migrations\__init__.py"
    )
)

echo [OK] Migration dependencies checked

REM Delete old migrations if fresh migration
if "%FRESH_MIGRATION%"=="true" (
    echo.
    echo [INFO] Removing old migrations...
    for /d %%d in (apps\*\migrations) do (
        for %%f in ("%%d\*.py") do (
            if not "%%~nf"=="__init__" (
                del "%%f"
                echo [OK] Removed %%f
            )
        )
    )
)

REM Check for migration conflicts
echo.
echo [INFO] Checking for migration conflicts...
python manage.py makemigrations --check --dry-run 2>nul
if errorlevel 1 (
    echo [INFO] There are changes that need migrations
)

REM Create migrations for each app in dependency order
echo.
echo [INFO] Creating migrations...

REM Order matters - dependencies first!
set "APPS=users programs sessions students grades attendance ml predictions alerts"

for %%a in (%APPS%) do (
    echo [INFO] Creating migrations for apps.%%a...
    python manage.py makemigrations %%a --noinput 2>nul
    if errorlevel 1 (
        echo [INFO] No changes detected for apps.%%a
    )
)

REM Create any remaining migrations
echo.
echo [INFO] Creating remaining migrations...
python manage.py makemigrations --noinput

REM Show migration plan
echo.
echo [INFO] Migration plan:
python manage.py showmigrations

REM Apply migrations
echo.
echo [INFO] Applying migrations...
python manage.py migrate --noinput
if errorlevel 1 (
    echo [ERROR] Migration failed!
    exit /b 1
)

REM Verify migrations
echo.
echo [INFO] Verifying migrations...
python manage.py showmigrations

REM Create cache tables if using database cache
findstr /C:"django.core.cache.backends.db" config\settings.py >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [INFO] Creating cache tables...
    python manage.py createcachetable 2>nul
)

REM Collect static files (if not in development)
if not "%DEBUG%"=="True" (
    echo.
    echo [INFO] Collecting static files...
    python manage.py collectstatic --noinput
)

echo.
echo ========================================
echo [SUCCESS] Migrations completed successfully!
echo ========================================

echo.
echo Next steps:
echo   1. Create superuser: python manage.py createsuperuser
echo   2. Load initial data: python manage.py loaddata fixtures\*.json
echo   3. Start development server: python manage.py runserver
echo.
pause
