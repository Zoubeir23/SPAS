#!/bin/bash
# ============================================
# SPAS - Database Initialization Script (Linux/Mac)
# ============================================
# This script initializes the PostgreSQL database for SPAS
# Usage: ./scripts/init_db.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SPAS Database Initialization${NC}"
echo -e "${GREEN}========================================${NC}"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓${NC} Environment variables loaded"
else
    echo -e "${RED}✗${NC} .env file not found!"
    echo -e "${YELLOW}→${NC} Copy .env.example to .env and configure it"
    exit 1
fi

# Default values if not set
DB_NAME=${DB_NAME:-spas_db}
DB_USER=${DB_USER:-spas_user}
DB_PASSWORD=${DB_PASSWORD:-your_password}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo -e "\n${YELLOW}Database Configuration:${NC}"
echo -e "  Name: ${DB_NAME}"
echo -e "  User: ${DB_USER}"
echo -e "  Host: ${DB_HOST}"
echo -e "  Port: ${DB_PORT}"

# Check if PostgreSQL is running
echo -e "\n${YELLOW}Checking PostgreSQL service...${NC}"
if ! pg_isready -h ${DB_HOST} -p ${DB_PORT} > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} PostgreSQL is not running on ${DB_HOST}:${DB_PORT}"
    echo -e "${YELLOW}→${NC} Start PostgreSQL and try again"
    exit 1
fi
echo -e "${GREEN}✓${NC} PostgreSQL is running"

# Create database user (if not exists)
echo -e "\n${YELLOW}Creating database user...${NC}"
sudo -u postgres psql -c "SELECT 1 FROM pg_user WHERE usename = '${DB_USER}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"
echo -e "${GREEN}✓${NC} Database user ready"

# Create database (if not exists)
echo -e "\n${YELLOW}Creating database...${NC}"
sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw ${DB_NAME} || \
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
echo -e "${GREEN}✓${NC} Database created"

# Grant privileges
echo -e "\n${YELLOW}Granting privileges...${NC}"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
sudo -u postgres psql -d ${DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${DB_USER};"
echo -e "${GREEN}✓${NC} Privileges granted"

# Install required extensions
echo -e "\n${YELLOW}Installing PostgreSQL extensions...${NC}"
sudo -u postgres psql -d ${DB_NAME} -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
echo -e "${GREEN}✓${NC} Extensions installed"

# Run Django migrations
echo -e "\n${YELLOW}Running Django migrations...${NC}"
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}✓${NC} Migrations completed"

# Create superuser
echo -e "\n${YELLOW}Creating superuser...${NC}"
echo -e "${YELLOW}→${NC} You will be prompted to create an admin user"
python manage.py createsuperuser --username admin --email admin@spas.local || true

# Load initial data (if fixtures exist)
echo -e "\n${YELLOW}Loading initial data...${NC}"
if [ -d "fixtures" ]; then
    python manage.py loaddata fixtures/*.json 2>/dev/null || echo -e "${YELLOW}→${NC} No fixtures found"
else
    echo -e "${YELLOW}→${NC} No fixtures directory found"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Database initialization completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Start the development server: python manage.py runserver"
echo -e "  2. Access admin panel: http://localhost:8000/admin"
echo -e "  3. Login with the admin credentials you just created"
echo -e "\n"
