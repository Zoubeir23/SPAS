"""
Database Setup Script for SPAS
This script creates the PostgreSQL database and user with proper permissions.
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import environ

# Add the project root to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

# Database configuration
DB_NAME = env('DB_NAME', default='spas_db')
DB_USER = env('DB_USER', default='spas_user')
DB_PASSWORD = env('DB_PASSWORD', default='your_password')
DB_HOST = env('DB_HOST', default='localhost')
DB_PORT = env('DB_PORT', default='5432')

# PostgreSQL superuser (usually 'postgres')
POSTGRES_USER = env('POSTGRES_USER', default='postgres')
POSTGRES_PASSWORD = env('POSTGRES_PASSWORD', default='')


def print_success(message):
    """Print success message in green."""
    print(f"\033[92m✓ {message}\033[0m")


def print_error(message):
    """Print error message in red."""
    print(f"\033[91m✗ {message}\033[0m")


def print_info(message):
    """Print info message in yellow."""
    print(f"\033[93m→ {message}\033[0m")


def print_header(message):
    """Print header message."""
    print(f"\n\033[94m{'='*60}\033[0m")
    print(f"\033[94m{message}\033[0m")
    print(f"\033[94m{'='*60}\033[0m\n")


def connect_postgres():
    """Connect to PostgreSQL as superuser."""
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print_success("Connected to PostgreSQL server")
        return conn
    except psycopg2.OperationalError as e:
        print_error(f"Failed to connect to PostgreSQL: {e}")
        print_info("Make sure PostgreSQL is running and credentials are correct")
        sys.exit(1)


def user_exists(cursor, username):
    """Check if database user exists."""
    cursor.execute(
        "SELECT 1 FROM pg_user WHERE usename = %s",
        (username,)
    )
    return cursor.fetchone() is not None


def database_exists(cursor, dbname):
    """Check if database exists."""
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (dbname,)
    )
    return cursor.fetchone() is not None


def create_user(cursor):
    """Create database user if it doesn't exist."""
    if user_exists(cursor, DB_USER):
        print_info(f"User '{DB_USER}' already exists")
        # Update password just in case
        cursor.execute(
            sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                sql.Identifier(DB_USER)
            ),
            (DB_PASSWORD,)
        )
        print_success(f"User '{DB_USER}' password updated")
    else:
        cursor.execute(
            sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                sql.Identifier(DB_USER)
            ),
            (DB_PASSWORD,)
        )
        print_success(f"User '{DB_USER}' created")


def create_database(cursor):
    """Create database if it doesn't exist."""
    if database_exists(cursor, DB_NAME):
        print_info(f"Database '{DB_NAME}' already exists")
    else:
        cursor.execute(
            sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(DB_NAME),
                sql.Identifier(DB_USER)
            )
        )
        print_success(f"Database '{DB_NAME}' created")


def grant_privileges(cursor):
    """Grant necessary privileges to database user."""
    # Grant all privileges on database
    cursor.execute(
        sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(DB_NAME),
            sql.Identifier(DB_USER)
        )
    )
    print_success(f"Granted all privileges on database '{DB_NAME}' to '{DB_USER}'")


def setup_extensions(cursor):
    """Install required PostgreSQL extensions."""
    extensions = ['uuid-ossp', 'pg_trgm']  # pg_trgm for text search optimization

    for ext in extensions:
        try:
            cursor.execute(
                sql.SQL("CREATE EXTENSION IF NOT EXISTS {}").format(
                    sql.Identifier(ext.replace('-', '_'))
                )
            )
            print_success(f"Extension '{ext}' installed")
        except Exception as e:
            print_error(f"Failed to install extension '{ext}': {e}")


def grant_schema_privileges():
    """Grant privileges on schema public."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Grant privileges on schema public
        cursor.execute(
            sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
                sql.Identifier(DB_USER)
            )
        )

        # Grant default privileges for future tables
        cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
                sql.Identifier(DB_USER)
            )
        )

        # Install extensions
        setup_extensions(cursor)

        cursor.close()
        conn.close()
        print_success(f"Schema privileges granted to '{DB_USER}'")
    except Exception as e:
        print_error(f"Failed to grant schema privileges: {e}")


def main():
    """Main setup function."""
    print_header("SPAS Database Setup Script")

    print_info(f"Database Name: {DB_NAME}")
    print_info(f"Database User: {DB_USER}")
    print_info(f"Database Host: {DB_HOST}")
    print_info(f"Database Port: {DB_PORT}")

    # Connect to PostgreSQL
    conn = connect_postgres()
    cursor = conn.cursor()

    try:
        # Create user
        print("\n--- Creating Database User ---")
        create_user(cursor)

        # Create database
        print("\n--- Creating Database ---")
        create_database(cursor)

        # Grant privileges
        print("\n--- Granting Privileges ---")
        grant_privileges(cursor)

        cursor.close()
        conn.close()

        # Grant schema privileges and setup extensions
        print("\n--- Setting up Schema and Extensions ---")
        grant_schema_privileges()

        print_header("Database setup completed successfully!")
        print_info("Next steps:")
        print("  1. Run migrations: python manage.py migrate")
        print("  2. Create superuser: python manage.py createsuperuser")
        print("  3. Load fixtures: python manage.py loaddata fixtures/*.json")

    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
