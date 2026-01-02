@echo off
REM Script de configuration complete du backend SPAS
REM Execute toutes les etapes necessaires pour demarrer le projet

echo ============================================
echo   SPAS Backend - Configuration Complete
echo ============================================
echo.

REM Verifier si l'environnement virtuel existe
if not exist venv (
    echo [1/6] Creation de l'environnement virtuel...
    python -m venv venv
) else (
    echo [1/6] Environnement virtuel existe deja.
)

REM Activer l'environnement virtuel
echo [2/6] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dependances
echo [3/6] Installation des dependances...
pip install -r requirements.txt --quiet

REM Creer les migrations
echo [4/6] Creation des migrations...
python manage.py makemigrations users
python manage.py makemigrations students
python manage.py makemigrations programs
python manage.py makemigrations sessions
python manage.py makemigrations grades
python manage.py makemigrations attendance
python manage.py makemigrations ml
python manage.py makemigrations predictions
python manage.py makemigrations alerts

REM Appliquer les migrations
echo [5/6] Application des migrations...
python manage.py migrate

REM Creer les donnees initiales
echo [6/6] Creation des donnees initiales...
python manage.py init_spas

echo.
echo ============================================
echo   Configuration terminee avec succes!
echo ============================================
echo.
echo Prochaines etapes:
echo   1. Demarrer le serveur: python manage.py runserver
echo   2. Acceder a l'admin: http://localhost:8000/admin/
echo   3. Voir la doc API: http://localhost:8000/api/docs/
echo.
echo Identifiants:
echo   Admin: admin@spas.ca / admin123
echo   Prof: jean.dupont@spas.ca / teacher123
echo.

pause
