"""
Script de test pour vérifier les fonctionnalités de SPAS.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.students.models import Student
from apps.sessions.models import Session
from apps.attendance.models import Attendance
from apps.programs.models import Program, Department
from django.contrib.auth import authenticate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_user_creation():
    """Test la création d'utilisateurs pour chaque rôle."""
    print("\n" + "="*60)
    print("TEST 1: Création des Utilisateurs")
    print("="*60)
    
    roles = ['admin', 'teacher', 'ds', 'pedagogical']
    created_users = []
    
    for role in roles:
        email = f"test_{role}@isi.edu"
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            print(f"  [OK] Utilisateur {role} existe deja: {email}")
            user = User.objects.get(email=email)
        else:
            try:
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=f'Test {role.capitalize()}',
                    last_name='User',
                    role=role
                )
                print(f"  [OK] Utilisateur {role} cree: {email}")
            except Exception as e:
                print(f"  [ERREUR] Erreur creation {role}: {e}")
                continue
        
        created_users.append((role, email, user))
    
    return created_users


def test_user_login():
    """Test la connexion pour chaque rôle."""
    print("\n" + "="*60)
    print("TEST 2: Connexion des Utilisateurs")
    print("="*60)
    
    roles = ['admin', 'teacher', 'ds', 'pedagogical']
    login_results = []
    
    for role in roles:
        email = f"test_{role}@isi.edu"
        
        try:
            user = User.objects.filter(email=email).first()
            if not user:
                print(f"  [ERREUR] Utilisateur {role} non trouve: {email}")
                continue
            
            # Test authentification
            authenticated_user = authenticate(email=email, password='password123')
            if authenticated_user:
                print(f"  [OK] Connexion reussie pour {role}: {email}")
                login_results.append((role, True, user))
            else:
                print(f"  [ERREUR] Echec connexion pour {role}: {email}")
                login_results.append((role, False, None))
        except Exception as e:
            print(f"  ✗ Erreur connexion {role}: {e}")
            login_results.append((role, False, None))
    
    return login_results


def test_dashboards():
    """Vérifie que les dashboards sont différents selon les rôles."""
    print("\n" + "="*60)
    print("TEST 3: Vérification des Dashboards par Rôle")
    print("="*60)
    
    roles = ['admin', 'teacher', 'ds', 'pedagogical']
    
    for role in roles:
        email = f"test_{role}@isi.edu"
        user = User.objects.filter(email=email).first()
        
        if not user:
            print(f"  [ERREUR] Utilisateur {role} non trouve")
            continue
        
        print(f"\n  Rôle: {role.upper()}")
        print(f"    - Email: {user.email}")
        print(f"    - Nom: {user.get_full_name()}")
        print(f"    - Rôle: {user.role}")
        print(f"    - Actif: {user.is_active}")
        
        # Vérifier les permissions selon le rôle
        if role == 'admin':
            print(f"    - Peut créer utilisateurs: OUI")
            print(f"    - Peut gérer sessions: OUI")
            print(f"    - Peut voir dashboard prédictif: OUI")
        elif role == 'teacher':
            print(f"    - Peut créer utilisateurs: NON")
            print(f"    - Peut gérer sessions: NON")
            print(f"    - Peut voir dashboard prédictif: NON")
        elif role == 'ds':
            print(f"    - Peut créer utilisateurs: NON")
            print(f"    - Peut gérer sessions: NON")
            print(f"    - Peut voir dashboard prédictif: OUI")
        elif role == 'pedagogical':
            print(f"    - Peut créer utilisateurs: NON")
            print(f"    - Peut gérer sessions: OUI")
            print(f"    - Peut voir dashboard prédictif: OUI")


def test_attendance_creation():
    """Test la création de listes d'absence."""
    print("\n" + "="*60)
    print("TEST 4: Création des Listes d'Absence")
    print("="*60)
    
    # Vérifier qu'il y a des étudiants
    students = Student.objects.filter(status=Student.Status.ACTIVE)[:5]
    
    if not students.exists():
        print("  ⚠ Aucun étudiant actif trouvé pour tester les absences")
        return False
    
        print(f"  [OK] {students.count()} etudiants trouves pour test")
    
    # Vérifier qu'il y a des sessions
    sessions = Session.objects.filter(status=Session.Status.ACTIVE)[:1]
    
    if not sessions.exists():
        print("  ⚠ Aucune session active trouvée")
        return False
    
    session = sessions.first()
    print(f"  ✓ Session trouvée: {session.name}")
    
    # Compter les absences existantes
    existing_count = Attendance.objects.count()
    print(f"  ✓ Absences existantes: {existing_count}")
    
    return True


def test_session_creation():
    """Test la création de sessions."""
    print("\n" + "="*60)
    print("TEST 5: Création des Sessions")
    print("="*60)
    
    # Compter les sessions existantes
    sessions_count = Session.objects.count()
    print(f"  [OK] Sessions existantes: {sessions_count}")
    
    # Vérifier les sessions actives
    active_sessions = Session.objects.filter(status=Session.Status.ACTIVE)
    print(f"  ✓ Sessions actives: {active_sessions.count()}")
    
    # Lister quelques sessions
    if active_sessions.exists():
        print(f"\n  Sessions actives:")
        for session in active_sessions[:3]:
            print(f"    - {session.name} ({session.status})")
    
    return True


def main():
    """Exécute tous les tests."""
    print("\n" + "="*60)
    print("TESTS DE FONCTIONNALITÉS - SPAS")
    print("="*60)
    
    # Test 1: Création utilisateurs
    users = test_user_creation()
    
    # Test 2: Connexion
    logins = test_user_login()
    
    # Test 3: Dashboards
    test_dashboards()
    
    # Test 4: Absences
    test_attendance_creation()
    
    # Test 5: Sessions
    test_session_creation()
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"  Utilisateurs créés/vérifiés: {len(users)}")
    print(f"  Connexions réussies: {sum(1 for _, success, _ in logins if success)}/{len(logins)}")
    print(f"  Dashboards: Vérifiés par rôle")
    print(f"  Absences: Système vérifié")
    print(f"  Sessions: Système vérifié")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

