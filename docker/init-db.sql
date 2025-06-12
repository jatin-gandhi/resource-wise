-- Initialize Resource Wise Database
-- This script runs automatically when the container starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN indexes for full-text search (will be used by our models)
-- Note: These will be created on actual tables by Alembic migrations
-- This is just to ensure the extensions are available

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Resource Wise database initialized successfully';
    RAISE NOTICE 'Extensions enabled: vector, pg_trgm';
    RAISE NOTICE 'Ready for Alembic migrations';
END $$; 