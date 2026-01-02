"""
Migration Status Checker for SPAS
This script checks the status of migrations and identifies any issues.
"""

import os
import sys
from pathlib import Path
import django

# Add the project root to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.apps import apps
from django.db.migrations.loader import MigrationLoader


def print_success(message):
    """Print success message in green."""
    print(f"\033[92m✓ {message}\033[0m")


def print_error(message):
    """Print error message in red."""
    print(f"\033[91m✗ {message}\033[0m")


def print_warning(message):
    """Print warning message in yellow."""
    print(f"\033[93m⚠ {message}\033[0m")


def print_info(message):
    """Print info message in blue."""
    print(f"\033[94mℹ {message}\033[0m")


def print_header(message):
    """Print header message."""
    print(f"\n\033[94m{'='*70}\033[0m")
    print(f"\033[94m{message:^70}\033[0m")
    print(f"\033[94m{'='*70}\033[0m\n")


def check_database_connection():
    """Check if database connection is working."""
    try:
        connection.ensure_connection()
        print_success(f"Database connection successful")
        print_info(f"   Database: {connection.settings_dict['NAME']}")
        print_info(f"   Host: {connection.settings_dict['HOST']}")
        print_info(f"   Port: {connection.settings_dict['PORT']}")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def check_migrations_applied():
    """Check which migrations have been applied."""
    loader = MigrationLoader(connection)
    applied_migrations = loader.applied_migrations

    print_info(f"Total applied migrations: {len(applied_migrations)}")

    # Group by app
    by_app = {}
    for app, migration in applied_migrations:
        if app not in by_app:
            by_app[app] = []
        by_app[app].append(migration)

    for app in sorted(by_app.keys()):
        migrations = by_app[app]
        print_info(f"   {app}: {len(migrations)} migration(s)")

    return by_app


def check_unapplied_migrations():
    """Check for unapplied migrations."""
    loader = MigrationLoader(connection)
    graph = loader.graph

    unapplied = []
    for app_name in loader.migrated_apps:
        app_migrations = graph.leaf_nodes(app_name)
        for migration in app_migrations:
            if migration not in loader.applied_migrations:
                unapplied.append(migration)

    if unapplied:
        print_warning(f"Found {len(unapplied)} unapplied migration(s):")
        for app, migration in unapplied:
            print_warning(f"   {app}.{migration}")
    else:
        print_success("All migrations are applied")

    return unapplied


def check_migration_conflicts():
    """Check for migration conflicts."""
    try:
        loader = MigrationLoader(connection)
        conflicts = loader.detect_conflicts()

        if conflicts:
            print_error("Migration conflicts detected:")
            for app, migrations in conflicts.items():
                print_error(f"   {app}:")
                for migration in migrations:
                    print_error(f"      - {migration}")
            return True
        else:
            print_success("No migration conflicts detected")
            return False
    except Exception as e:
        print_error(f"Error checking conflicts: {e}")
        return True


def check_models_vs_migrations():
    """Check if models match migrations."""
    print_info("Checking if models match migrations...")

    # This will be caught by makemigrations --check
    try:
        from io import StringIO
        from django.core.management import call_command

        output = StringIO()
        call_command('makemigrations', '--check', '--dry-run', stdout=output)
        print_success("Models match migrations")
        return True
    except SystemExit:
        print_warning("Models have changes that need migrations")
        print_info("Run: python manage.py makemigrations")
        return False


def check_migration_files():
    """Check migration files in each app."""
    print_info("Checking migration files...")

    apps_config = apps.get_app_configs()
    total_files = 0

    for app_config in apps_config:
        if app_config.name.startswith('apps.'):
            migrations_dir = Path(app_config.path) / 'migrations'

            if not migrations_dir.exists():
                print_warning(f"   {app_config.name}: No migrations directory")
                continue

            migration_files = list(migrations_dir.glob('[0-9]*.py'))
            total_files += len(migration_files)

            if migration_files:
                print_info(f"   {app_config.name}: {len(migration_files)} migration file(s)")
            else:
                print_warning(f"   {app_config.name}: No migration files found")

    print_info(f"Total migration files: {total_files}")
    return total_files


def check_custom_user_model():
    """Check if custom user model is properly configured."""
    from django.conf import settings

    if hasattr(settings, 'AUTH_USER_MODEL'):
        print_success(f"Custom user model configured: {settings.AUTH_USER_MODEL}")

        # Check if migrations exist for users app
        try:
            User = apps.get_model(settings.AUTH_USER_MODEL)
            print_success(f"User model loaded successfully: {User.__name__}")
            return True
        except Exception as e:
            print_error(f"Failed to load user model: {e}")
            return False
    else:
        print_warning("No custom user model configured")
        return False


def main():
    """Run all migration checks."""
    print_header("SPAS Migration Status Checker")

    # Check database connection
    print_header("Database Connection")
    if not check_database_connection():
        print_error("\nCannot proceed without database connection")
        sys.exit(1)

    # Check custom user model
    print_header("User Model Configuration")
    check_custom_user_model()

    # Check migration files
    print_header("Migration Files")
    check_migration_files()

    # Check applied migrations
    print_header("Applied Migrations")
    check_migrations_applied()

    # Check unapplied migrations
    print_header("Unapplied Migrations")
    has_unapplied = len(check_unapplied_migrations()) > 0

    # Check conflicts
    print_header("Migration Conflicts")
    has_conflicts = check_migration_conflicts()

    # Check if models match migrations
    print_header("Model-Migration Consistency")
    models_match = check_models_vs_migrations()

    # Summary
    print_header("Summary")

    if has_conflicts:
        print_error("CRITICAL: Migration conflicts need to be resolved")
        print_info("   Run: python manage.py migrate --plan")
        status = "CONFLICTS"
    elif has_unapplied:
        print_warning("WARNING: Unapplied migrations found")
        print_info("   Run: python manage.py migrate")
        status = "PENDING"
    elif not models_match:
        print_warning("WARNING: Model changes need migrations")
        print_info("   Run: python manage.py makemigrations")
        status = "CHANGES"
    else:
        print_success("SUCCESS: All migrations are up to date")
        status = "OK"

    print_header(f"Status: {status}")


if __name__ == '__main__':
    main()
