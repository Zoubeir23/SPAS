@echo off
echo ========================================
echo SPAS Backend - Configuration Developpement
echo ========================================
echo.

echo 1. Creation de l'environnement virtuel...
python -m venv venv
echo.

echo 2. Activation de l'environnement virtuel...
call venv\Scripts\activate
echo.

echo 3. Installation des dependances...
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo 4. Creation du fichier .env...
if not exist .env (
    copy .env.example .env
    echo Fichier .env cree. Veuillez le configurer avant de continuer.
) else (
    echo Fichier .env existe deja.
)
echo.

echo 5. Creation des dossiers necessaires...
if not exist logs mkdir logs
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles
if not exist ml_models mkdir ml_models
echo.

echo ========================================
echo Configuration terminee!
echo ========================================
echo.
echo Prochaines etapes:
echo 1. Configurez votre fichier .env
echo 2. Creez la base de donnees PostgreSQL
echo 3. Executez: python manage.py migrate
echo 4. Executez: python manage.py createsuperuser
echo 5. Lancez le serveur: python manage.py runserver
echo.
pause
