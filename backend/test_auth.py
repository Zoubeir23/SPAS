#!/usr/bin/env python
"""
Script de test pour le système d'authentification SPAS.

Usage:
    python test_auth.py

Ce script teste les principaux endpoints d'authentification.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000/api/auth"

# Couleurs pour output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_password_strength():
    """Test la vérification de force de mot de passe."""
    print_info("Test 1: Vérification de force de mot de passe...")

    passwords = [
        ("weak", "Faible"),
        ("Password1!", "Moyen"),
        ("SecureP@ssw0rd123!", "Fort"),
    ]

    for password, expected in passwords:
        response = requests.post(
            f"{BASE_URL}/password/check-strength/",
            json={"password": password}
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Mot de passe '{password}': Score {data['score']}/100 - {data['strength']}")
        else:
            print_error(f"Erreur lors du test de '{password}'")

def test_registration():
    """Test l'inscription d'un nouvel utilisateur."""
    print_info("\nTest 2: Inscription d'un nouvel utilisateur...")

    user_data = {
        "email": "test.user@spas.com",
        "password": "SecureP@ssw0rd123!",
        "password_confirm": "SecureP@ssw0rd123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "teacher",
        "phone": "+1234567890"
    }

    response = requests.post(
        f"{BASE_URL}/register/",
        json=user_data
    )

    if response.status_code == 201:
        data = response.json()
        print_success("Utilisateur créé avec succès")
        print_info(f"Email: {data['user']['email']}")
        print_info(f"Token de vérification: {data.get('verification_token', 'N/A')[:20]}...")
        return data.get('verification_token')
    elif response.status_code == 400:
        error = response.json()
        if 'email' in error and 'existe déjà' in str(error['email']):
            print_warning("L'utilisateur existe déjà (normal si vous exécutez ce script plusieurs fois)")
            return None
        else:
            print_error(f"Erreur d'inscription: {error}")
            return None
    else:
        print_error(f"Erreur d'inscription: {response.status_code}")
        return None

def test_login_without_verification():
    """Test de connexion sans vérification d'email."""
    print_info("\nTest 3: Tentative de connexion sans vérification...")

    response = requests.post(
        f"{BASE_URL}/login/",
        json={
            "email": "test.user@spas.com",
            "password": "SecureP@ssw0rd123!"
        }
    )

    if response.status_code == 400:
        print_success("Connexion correctement refusée (email non vérifié)")
    else:
        print_warning("Connexion autorisée malgré email non vérifié")

def test_email_verification(token):
    """Test la vérification d'email."""
    if not token:
        print_warning("\nTest 4: Ignoré (pas de token)")
        return False

    print_info("\nTest 4: Vérification d'email...")

    response = requests.post(
        f"{BASE_URL}/verify-email/",
        json={"token": token}
    )

    if response.status_code == 200:
        print_success("Email vérifié avec succès")
        return True
    else:
        print_error(f"Erreur de vérification: {response.json()}")
        return False

def test_login():
    """Test de connexion après vérification."""
    print_info("\nTest 5: Connexion après vérification...")

    response = requests.post(
        f"{BASE_URL}/login/",
        json={
            "email": "test.user@spas.com",
            "password": "SecureP@ssw0rd123!"
        }
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Connexion réussie")
        print_info(f"Access token: {data['access'][:30]}...")
        print_info(f"Refresh token: {data['refresh'][:30]}...")
        return data['access'], data['refresh']
    else:
        print_error(f"Erreur de connexion: {response.json()}")
        return None, None

def test_authenticated_request(access_token):
    """Test une requête authentifiée."""
    if not access_token:
        print_warning("\nTest 6: Ignoré (pas de token)")
        return

    print_info("\nTest 6: Requête authentifiée (GET /me)...")

    response = requests.get(
        f"{BASE_URL}/me/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print_success(f"Utilisateur: {data['first_name']} {data['last_name']} ({data['email']})")
        print_info(f"Rôle: {data['role']}")
    else:
        print_error(f"Erreur: {response.status_code}")

def test_token_refresh(refresh_token):
    """Test le rafraîchissement de token."""
    if not refresh_token:
        print_warning("\nTest 7: Ignoré (pas de token)")
        return None

    print_info("\nTest 7: Rafraîchissement de token...")

    response = requests.post(
        f"{BASE_URL}/token/refresh/",
        json={"refresh": refresh_token}
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Token rafraîchi avec succès")
        print_info(f"Nouveau access token: {data['access'][:30]}...")
        return data['access']
    else:
        print_error(f"Erreur: {response.json()}")
        return None

def test_brute_force_protection():
    """Test la protection contre brute force."""
    print_info("\nTest 8: Protection contre brute force (5 tentatives échouées)...")

    for i in range(6):
        response = requests.post(
            f"{BASE_URL}/login/",
            json={
                "email": "test.user@spas.com",
                "password": "WrongPassword123!"
            }
        )

        if i < 5:
            print_info(f"Tentative {i+1}/5 échouée (normal)")
        else:
            if response.status_code == 400 and 'verrouillé' in str(response.json()):
                print_success("Compte verrouillé après 5 tentatives (protection active)")
            else:
                print_warning("Compte non verrouillé (vérifier la configuration)")

        sleep(0.5)  # Petit délai entre tentatives

def test_logout(access_token, refresh_token):
    """Test la déconnexion."""
    if not access_token or not refresh_token:
        print_warning("\nTest 9: Ignoré (pas de tokens)")
        return

    print_info("\nTest 9: Déconnexion...")

    response = requests.post(
        f"{BASE_URL}/logout/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh": refresh_token}
    )

    if response.status_code == 200:
        print_success("Déconnexion réussie")
    else:
        print_error(f"Erreur: {response.json()}")

def test_activity_log(access_token):
    """Test la récupération de l'historique d'activité."""
    if not access_token:
        print_warning("\nTest 10: Ignoré (pas de token)")
        return

    print_info("\nTest 10: Historique d'activité...")

    response = requests.get(
        f"{BASE_URL}/activity/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        print_success(f"{len(events)} événements trouvés")
        for event in events[-3:]:  # Derniers 3 événements
            print_info(f"  - {event.get('event')}: {event.get('timestamp', 'N/A')[:19]}")
    else:
        print_error(f"Erreur: {response.status_code}")

def main():
    """Fonction principale."""
    print("\n" + "="*60)
    print("TESTS DU SYSTÈME D'AUTHENTIFICATION SPAS")
    print("="*60)

    try:
        # Test 1: Password strength
        test_password_strength()

        # Test 2: Registration
        verification_token = test_registration()

        # Test 3: Login without verification
        test_login_without_verification()

        # Test 4: Email verification
        if verification_token:
            verified = test_email_verification(verification_token)
        else:
            # Utiliser un compte déjà vérifié pour continuer les tests
            print_warning("\nUtilisation d'un compte existant pour les tests suivants...")
            verified = True

        # Test 5: Login
        access_token, refresh_token = test_login()

        # Test 6: Authenticated request
        test_authenticated_request(access_token)

        # Test 7: Token refresh
        new_access_token = test_token_refresh(refresh_token)

        # Test 8: Activity log
        test_activity_log(new_access_token or access_token)

        # Test 9: Brute force protection
        test_brute_force_protection()

        # Test 10: Logout
        test_logout(new_access_token or access_token, refresh_token)

        print("\n" + "="*60)
        print_success("TESTS TERMINÉS")
        print("="*60 + "\n")

    except requests.exceptions.ConnectionError:
        print_error("\nImpossible de se connecter au serveur.")
        print_info("Assurez-vous que le serveur Django est démarré:")
        print_info("  python manage.py runserver")
    except Exception as e:
        print_error(f"\nErreur inattendue: {str(e)}")

if __name__ == "__main__":
    main()
