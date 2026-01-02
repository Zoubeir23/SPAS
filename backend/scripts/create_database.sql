-- ============================================
-- SPAS - Script de création de la base de données PostgreSQL
-- ============================================
-- Exécuter en tant que superuser postgres:
--   psql -U postgres -f create_database.sql
-- ============================================

-- Supprimer la base de données si elle existe (optionnel - décommenter si nécessaire)
-- DROP DATABASE IF EXISTS spas_db;
-- DROP USER IF EXISTS spas_user;

-- Créer l'utilisateur dédié pour SPAS
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'spas_user') THEN
        CREATE USER spas_user WITH PASSWORD 'passer';
        RAISE NOTICE 'Utilisateur spas_user créé avec succès';
    ELSE
        RAISE NOTICE 'Utilisateur spas_user existe déjà';
    END IF;
END
$$;

-- Créer la base de données
SELECT 'CREATE DATABASE spas_db OWNER spas_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spas_db')\gexec

-- Accorder tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;

-- Se connecter à la base spas_db pour configurer les extensions
\c spas_db

-- Créer les extensions utiles (optionnel mais recommandé)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Pour la recherche textuelle

-- Accorder les droits sur le schéma public
GRANT ALL ON SCHEMA public TO spas_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spas_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spas_user;

-- Configurer les droits par défaut pour les nouvelles tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO spas_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO spas_user;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Base de données SPAS configurée avec succès!';
    RAISE NOTICE '  Base: spas_db';
    RAISE NOTICE '  User: spas_user';
    RAISE NOTICE '  Pass: passer (à changer en production!)';
    RAISE NOTICE '============================================';
END
$$;
