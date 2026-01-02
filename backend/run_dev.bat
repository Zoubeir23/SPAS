@echo off
echo ========================================
echo SPAS Backend - Demarrage Serveur Dev
echo ========================================
echo.

echo Activation de l'environnement virtuel...
call venv\Scripts\activate
echo.

echo Verification des migrations...
python manage.py migrate
echo.

echo Demarrage du serveur Django...
python manage.py runserver
