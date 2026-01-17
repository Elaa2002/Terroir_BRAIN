-- ========================================
-- Terroir Brain - PostgreSQL Initialization
-- ========================================

-- Create auth database (not auto-created)
CREATE DATABASE terroir_auth;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE terroir_auth TO terroir;
GRANT ALL PRIVILEGES ON DATABASE terroir_main TO terroir;

-- Connect to main database
\c terroir_main

-- Enable useful PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Documentation comments
COMMENT ON DATABASE terroir_main IS
'Main database for Terroir Brain API - Cultural demand forecasting';

COMMENT ON DATABASE terroir_auth IS
'Authentication database for user management and JWT tokens';
