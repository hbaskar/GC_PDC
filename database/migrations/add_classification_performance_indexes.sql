-- Performance Optimization Indexes for Classifications
-- Run these commands in your database to improve query performance

-- Index for active classifications by level (most common filter combination)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_active_level')
CREATE INDEX idx_pdc_classifications_active_level 
ON pdc_classifications(is_active, classification_level) 
WHERE is_deleted = 0;

-- Index for organization-based queries with active status
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_org_active')
CREATE INDEX idx_pdc_classifications_org_active 
ON pdc_classifications(organization_id, is_active) 
WHERE is_deleted = 0;

-- Index for date-based sorting (newest first) - crucial for cursor pagination
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_created_desc')
CREATE INDEX idx_pdc_classifications_created_desc 
ON pdc_classifications(created_at DESC, classification_id) 
WHERE is_deleted = 0;

-- Index for name-based searches and sorting
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_name')
CREATE INDEX idx_pdc_classifications_name 
ON pdc_classifications(name) 
WHERE is_deleted = 0;

-- Unique index for code lookups (frequently used)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_code_unique')
CREATE INDEX idx_pdc_classifications_code_unique 
ON pdc_classifications(code) 
WHERE is_deleted = 0;

-- Composite index for sensitivity rating queries
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_sensitivity')
CREATE INDEX idx_pdc_classifications_sensitivity 
ON pdc_classifications(sensitivity_rating, is_active) 
WHERE is_deleted = 0;

-- Index for media type filtering
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_media_type')
CREATE INDEX idx_pdc_classifications_media_type 
ON pdc_classifications(media_type, is_active) 
WHERE is_deleted = 0;

-- Composite index for retention policy joins (reduces join cost)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_retention')
CREATE INDEX idx_pdc_classifications_retention 
ON pdc_classifications(retention_policy_id, is_active) 
WHERE is_deleted = 0;

-- Index for template-based queries
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_template')
CREATE INDEX idx_pdc_classifications_template 
ON pdc_classifications(template_id, is_active) 
WHERE is_deleted = 0 AND template_id IS NOT NULL;

-- Covering index for minimal responses (includes most commonly requested fields)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pdc_classifications_minimal_covering')
CREATE INDEX idx_pdc_classifications_minimal_covering 
ON pdc_classifications(is_active, classification_level) 
INCLUDE (classification_id, code, name, organization_id, created_at)
WHERE is_deleted = 0;

-- Performance monitoring view to track index usage
CREATE OR ALTER VIEW v_pdc_classification_index_usage AS
SELECT 
    i.name AS index_name,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates,
    s.last_user_seek,
    s.last_user_scan,
    s.last_user_lookup,
    (s.user_seeks + s.user_scans + s.user_lookups) AS total_reads,
    CASE 
        WHEN s.user_updates > 0 
        THEN CAST((s.user_seeks + s.user_scans + s.user_lookups) AS FLOAT) / s.user_updates
        ELSE NULL
    END AS reads_per_write
FROM sys.dm_db_index_usage_stats s
INNER JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE s.database_id = DB_ID() 
  AND OBJECT_NAME(s.object_id) = 'pdc_classifications'
  AND i.name LIKE 'idx_pdc_classifications_%'
ORDER BY total_reads DESC;

PRINT 'Classification performance indexes created successfully!'
PRINT 'Run "SELECT * FROM v_pdc_classification_index_usage" to monitor index usage.'