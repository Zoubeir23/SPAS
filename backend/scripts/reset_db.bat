@echo off
REM ============================================
REM SPAS - Database Reset Script (Windows)
REM ============================================
REM This script completely resets the database
REM WARNING: This will DELETE all data!
REM Usage: scripts\reset_db.bat

setlocal enabledelayedexpansion

echo ========================================
echo SPAS Database Reset
echo ========================================
echo WARNING: This will DELETE ALL data!
echo ========================================

REM Confirmation prompt
set /p confirm="Are you sure you want to reset the database? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo [INFO] Database reset cancelled
    exit /b 0
)

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    exit /b 1
)

REM Load environment variables
for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
    )
)

REM Set default values
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

REM Drop existing database
echo.
echo [INFO] Dropping existing database...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "DROP DATABASE IF EXISTS %DB_NAME%;" 2>nul
echo [OK] Database dropped

REM Drop existing user
echo.
echo [INFO] Dropping existing user...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "DROP USER IF EXISTS %DB_USER%;" 2>nul
echo [OK] User dropped

REM Remove migration files
echo.
echo [INFO] Removing migration files...
for /r apps %%i in (migrations\*.py) do (
    if not "%%~nxi"=="__init__.py" (
        del "%%i" 2>nul
    )
)
for /r apps %%i in (migrations\*.pyc) do del "%%i" 2>nul
echo [OK] Migration files removed

REM Remove SQLite database if exists
echo.
echo [INFO] Cleaning up...
if exist db.sqlite3 del db.sqlite3
echo [OK] Cleanup completed

REM Reinitialize database
echo.
echo ========================================
echo Reinitializing database...
echo ========================================
echo.

REM Call init_db.bat
call scripts\init_db.bat

echo.
echo ========================================
echo [SUCCESS] Database reset completed!
echo ========================================
pause
