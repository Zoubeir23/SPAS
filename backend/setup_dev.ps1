# SPAS Backend - Setup Script (PowerShell)
# Usage: .\setup_dev.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SPAS Backend - Configuration Developpement" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python version
Write-Host "1. Verification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   $pythonVersion trouve" -ForegroundColor Green

    # Check if version is 3.11+
    if ($pythonVersion -match "Python 3\.([0-9]+)") {
        $minorVersion = [int]$Matches[1]
        if ($minorVersion -lt 11) {
            Write-Host "   ATTENTION: Python 3.11+ recommande (actuel: $pythonVersion)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ERREUR: Python n'est pas installe ou n'est pas dans le PATH" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Create virtual environment
Write-Host "2. Creation de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   Environnement virtuel existe deja" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "   Environnement virtuel cree" -ForegroundColor Green
}
Write-Host ""

# 3. Activate virtual environment and install dependencies
Write-Host "3. Installation des dependances..." -ForegroundColor Yellow
& venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Host "   Dependances installees" -ForegroundColor Green
Write-Host ""

# 4. Create .env file
Write-Host "4. Configuration du fichier .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   Fichier .env existe deja" -ForegroundColor Green
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "   Fichier .env cree a partir de .env.example" -ForegroundColor Green
    Write-Host "   IMPORTANT: Veuillez configurer .env avant de continuer!" -ForegroundColor Yellow
}
Write-Host ""

# 5. Create necessary directories
Write-Host "5. Creation des dossiers necessaires..." -ForegroundColor Yellow
$directories = @("logs", "media", "staticfiles", "ml_models")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "   Dossier $dir cree" -ForegroundColor Green
    } else {
        Write-Host "   Dossier $dir existe deja" -ForegroundColor Gray
    }
}
Write-Host ""

# 6. Check PostgreSQL
Write-Host "6. Verification PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>&1
    Write-Host "   $pgVersion trouve" -ForegroundColor Green
} catch {
    Write-Host "   ATTENTION: PostgreSQL n'est pas detecte" -ForegroundColor Yellow
    Write-Host "   Assurez-vous que PostgreSQL est installe et configure" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration terminee!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "1. Configurez votre fichier .env avec vos parametres" -ForegroundColor White
Write-Host "2. Creez la base de donnees PostgreSQL:" -ForegroundColor White
Write-Host "   CREATE DATABASE spas_db;" -ForegroundColor Gray
Write-Host "   CREATE USER spas_user WITH PASSWORD 'spas_password';" -ForegroundColor Gray
Write-Host "   GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;" -ForegroundColor Gray
Write-Host "3. Appliquez les migrations:" -ForegroundColor White
Write-Host "   python manage.py migrate" -ForegroundColor Gray
Write-Host "4. Creez les donnees de test:" -ForegroundColor White
Write-Host "   python manage.py init_spas" -ForegroundColor Gray
Write-Host "5. Lancez le serveur:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "- Guide rapide: QUICKSTART.md" -ForegroundColor White
Write-Host "- Documentation API: API_GUIDE.md" -ForegroundColor White
Write-Host "- Documentation complete: README.md" -ForegroundColor White
Write-Host ""

# Keep window open
Read-Host "Appuyez sur Entree pour continuer..."
