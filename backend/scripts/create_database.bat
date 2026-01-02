@echo off
REM ============================================
REM SPAS - Script de création de la base PostgreSQL
REM ============================================
REM Prérequis: PostgreSQL installé et psql accessible dans le PATH
REM ============================================

echo ============================================
echo   SPAS - Creation Base de Donnees PostgreSQL
echo ============================================
echo.

REM Demander le mot de passe postgres si nécessaire
set /p PGPASSWORD="Entrez le mot de passe postgres (ou appuyez sur Entree si pas de mot de passe): "

REM Configuration
set DB_NAME=spas_db
set DB_USER=spas_user
set DB_PASSWORD=passer
set PG_HOST=localhost
set PG_PORT=5432

echo.
echo [1/4] Verification de la connexion PostgreSQL...
psql -U postgres -h %PG_HOST% -p %PG_PORT% -c "SELECT version();" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Impossible de se connecter a PostgreSQL.
    echo Verifiez que PostgreSQL est demarre et que psql est dans le PATH.
    pause
    exit /b 1
)
echo OK - Connexion PostgreSQL etablie.

echo.
echo [2/4] Creation de l'utilisateur %DB_USER%...
psql -U postgres -h %PG_HOST% -p %PG_PORT% -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '%DB_USER%') THEN CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%'; END IF; END $$;"

echo.
echo [3/4] Creation de la base de donnees %DB_NAME%...
psql -U postgres -h %PG_HOST% -p %PG_PORT% -c "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'" | findstr "1" > nul
if %ERRORLEVEL% NEQ 0 (
    psql -U postgres -h %PG_HOST% -p %PG_PORT% -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;"
    echo Base de donnees creee.
) else (
    echo Base de donnees existe deja.
)

echo.
echo [4/4] Attribution des privileges...
psql -U postgres -h %PG_HOST% -p %PG_PORT% -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
psql -U postgres -h %PG_HOST% -p %PG_PORT% -d %DB_NAME% -c "GRANT ALL ON SCHEMA public TO %DB_USER%;"

echo.
echo ============================================
echo   Base de donnees creee avec succes!
echo ============================================
echo.
echo Configuration:
echo   Host: %PG_HOST%
echo   Port: %PG_PORT%
echo   Database: %DB_NAME%
echo   User: %DB_USER%
echo   Password: %DB_PASSWORD%
echo.
echo Prochaine etape: 
echo   cd backend
echo   python manage.py migrate
echo.

set PGPASSWORD=
pause
