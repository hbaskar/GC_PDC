-- Migration: Add retention policy fields to pdc_classifications table
-- Date: 2025-11-13
-- Description: Add denormalized retention policy fields to classifications table for performance

BEGIN TRANSACTION;

-- Add retention policy columns to pdc_classifications table
ALTER TABLE pdc_classifications 
ADD 
    retention_code VARCHAR(50) NULL,
    retention_type VARCHAR(50) NULL,
    trigger_event VARCHAR(50) NULL,
    min_retention_years INT NULL,
    max_retention_years INT NULL,
    legal_hold_flag BIT NULL DEFAULT 0,
    destruction_method VARCHAR(100) NULL,
    review_frequency VARCHAR(50) NULL;

-- Update existing records with retention policy data from the related table
UPDATE c 
SET 
    c.retention_code = r.retention_code,
    c.retention_type = r.retention_type,
    c.trigger_event = r.trigger_event,
    c.min_retention_years = r.min_retention_years,
    c.max_retention_years = r.max_retention_years,
    c.legal_hold_flag = r.legal_hold_flag,
    c.destruction_method = r.destruction_method,
    c.review_frequency = r.review_frequency
FROM pdc_classifications c
INNER JOIN pdc_retention_policies r ON c.retention_policy_id = r.retention_policy_id
WHERE c.retention_policy_id IS NOT NULL;

-- Add indexes for better query performance on retention fields
CREATE INDEX IX_pdc_classifications_retention_type ON pdc_classifications(retention_type);
CREATE INDEX IX_pdc_classifications_retention_code ON pdc_classifications(retention_code);
CREATE INDEX IX_pdc_classifications_min_retention_years ON pdc_classifications(min_retention_years);

COMMIT TRANSACTION;

PRINT 'Successfully added retention policy fields to pdc_classifications table';