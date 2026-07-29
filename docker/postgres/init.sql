-- =============================================================================
-- CloudPulse AI — PostgreSQL Initialization
-- =============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cloudpulse TO cloudpulse_user;
