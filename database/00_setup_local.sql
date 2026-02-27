-- ============================================================
-- Local Development Setup
-- Run this as PostgreSQL superuser (postgres):
--   psql -U postgres -f database/00_setup_local.sql
-- ============================================================

-- Create user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'posuser') THEN
        CREATE ROLE posuser WITH LOGIN PASSWORD 'pospassword';
    END IF;
END
$$;

-- Create database
SELECT 'CREATE DATABASE posdb OWNER posuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'posdb')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE posdb TO posuser;
