# ============================================
# SPAS - Script de création de la base PostgreSQL (PowerShell)
# ============================================
# Prérequis: PostgreSQL installé et psql accessible dans le PATH
# Usage: .\create_database.ps1
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SPAS - Creation Base de Donnees PostgreSQL" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$DB_NAME = "spas_db"
$DB_USER = "spas_user"
$DB_PASSWORD = "passer"
$PG_HOST = "localhost"
$PG_PORT = "5432"

# Demander le mot de passe postgres
$pgPassword = Read-Host "Entrez le mot de passe postgres (ou appuyez sur Entree si pas de mot de passe)" -AsSecureString
$env:PGPASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pgPassword))

Write-Host ""
Write-Host "[1/5] Verification de la connexion PostgreSQL..." -ForegroundColor Yellow

try {
    $version = psql -U postgres -h $PG_HOST -p $PG_PORT -t -c "SELECT version();" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Connection failed" }
    Write-Host "OK - Connexion PostgreSQL etablie." -ForegroundColor Green
}
catch {
    Write-Host "ERREUR: Impossible de se connecter a PostgreSQL." -ForegroundColor Red
    Write-Host "Verifiez que PostgreSQL est demarre et que psql est dans le PATH." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] Creation de l'utilisateur $DB_USER..." -ForegroundColor Yellow
$createUserSQL = @"
DO `$`$ 
BEGIN 
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN 
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'; 
        RAISE NOTICE 'Utilisateur cree';
    ELSE 
        RAISE NOTICE 'Utilisateur existe deja';
    END IF; 
END 
`$`$;
"@
psql -U postgres -h $PG_HOST -p $PG_PORT -c $createUserSQL

Write-Host ""
Write-Host "[3/5] Creation de la base de donnees $DB_NAME..." -ForegroundColor Yellow
$dbExists = psql -U postgres -h $PG_HOST -p $PG_PORT -t -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" 2>$null
if ($dbExists -notmatch "1") {
    psql -U postgres -h $PG_HOST -p $PG_PORT -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    Write-Host "Base de donnees creee." -ForegroundColor Green
}
else {
    Write-Host "Base de donnees existe deja." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] Attribution des privileges..." -ForegroundColor Yellow
psql -U postgres -h $PG_HOST -p $PG_PORT -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -U postgres -h $PG_HOST -p $PG_PORT -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
psql -U postgres -h $PG_HOST -p $PG_PORT -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
psql -U postgres -h $PG_HOST -p $PG_PORT -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

Write-Host ""
Write-Host "[5/5] Installation des extensions..." -ForegroundColor Yellow
psql -U postgres -h $PG_HOST -p $PG_PORT -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# Nettoyer
$env:PGPASSWORD = ""

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Base de donnees creee avec succes!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Host: $PG_HOST"
Write-Host "  Port: $PG_PORT"
Write-Host "  Database: $DB_NAME"
Write-Host "  User: $DB_USER"
Write-Host "  Password: $DB_PASSWORD"
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  cd backend"
Write-Host "  .\venv\Scripts\activate"
Write-Host "  python manage.py makemigrations"
Write-Host "  python manage.py migrate"
Write-Host "  python manage.py init_spas"
Write-Host ""

Read-Host "Appuyez sur Entree pour fermer"
