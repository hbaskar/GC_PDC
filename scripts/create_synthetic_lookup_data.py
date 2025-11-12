#!/usr/bin/env python3
"""
Create synthetic data for PDC lookup_types and lookup_codes tables.
Based on the metadata identified from the API endpoints and existing data patterns.
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.config import get_engine
from sqlalchemy import text, inspect
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_comprehensive_lookup_data():
    """Get comprehensive lookup data based on API endpoints and existing patterns."""
    
    # Based on the pdc_classifications table structure and API endpoints
    lookup_data = {
        'CLASSIFICATION_LEVEL': {
            'display_name': 'Classification Level',
            'description': 'Security classification levels for documents and records',
            'codes': [
                {'code': 'PUBLIC', 'display_name': 'Public', 'description': 'Information that can be freely shared', 'sort_order': 1},
                {'code': 'INTERNAL', 'display_name': 'Internal Use', 'description': 'Information for internal organizational use only', 'sort_order': 2},
                {'code': 'CONFIDENTIAL', 'display_name': 'Confidential', 'description': 'Sensitive information requiring protection', 'sort_order': 3},
                {'code': 'RESTRICTED', 'display_name': 'Restricted', 'description': 'Highly sensitive information with limited access', 'sort_order': 4},
                {'code': 'SECRET', 'display_name': 'Secret', 'description': 'Top secret information requiring highest security', 'sort_order': 5}
            ]
        },
        'MEDIA_TYPE': {
            'display_name': 'Media Type',
            'description': 'Types of media formats for storing information',
            'codes': [
                {'code': 'PAPER', 'display_name': 'Paper Documents', 'description': 'Physical paper-based documents', 'sort_order': 1},
                {'code': 'ELECTRONIC', 'display_name': 'Electronic Files', 'description': 'Digital files and documents', 'sort_order': 2},
                {'code': 'MICROFILM', 'display_name': 'Microfilm', 'description': 'Microfilm storage medium', 'sort_order': 3},
                {'code': 'MICROFICHE', 'display_name': 'Microfiche', 'description': 'Microfiche storage cards', 'sort_order': 4},
                {'code': 'OPTICAL', 'display_name': 'Optical Media', 'description': 'CD, DVD, and other optical storage', 'sort_order': 5},
                {'code': 'MAGNETIC', 'display_name': 'Magnetic Media', 'description': 'Magnetic tape and disk storage', 'sort_order': 6},
                {'code': 'HYBRID', 'display_name': 'Hybrid Format', 'description': 'Combination of multiple media types', 'sort_order': 7}
            ]
        },
        'FILE_TYPE': {
            'display_name': 'File Type',
            'description': 'Categories of file types and document formats',
            'codes': [
                {'code': 'PDF', 'display_name': 'PDF Documents', 'description': 'Portable Document Format files', 'sort_order': 1},
                {'code': 'DOCX', 'display_name': 'Word Documents', 'description': 'Microsoft Word document files', 'sort_order': 2},
                {'code': 'XLSX', 'display_name': 'Excel Spreadsheets', 'description': 'Microsoft Excel spreadsheet files', 'sort_order': 3},
                {'code': 'PPTX', 'display_name': 'PowerPoint Presentations', 'description': 'Microsoft PowerPoint presentation files', 'sort_order': 4},
                {'code': 'TXT', 'display_name': 'Text Files', 'description': 'Plain text document files', 'sort_order': 5},
                {'code': 'HTML', 'display_name': 'HTML Documents', 'description': 'HyperText Markup Language files', 'sort_order': 6},
                {'code': 'XML', 'display_name': 'XML Documents', 'description': 'eXtensible Markup Language files', 'sort_order': 7},
                {'code': 'IMAGE', 'display_name': 'Image Files', 'description': 'JPEG, PNG, GIF and other image formats', 'sort_order': 8}
            ]
        },
        'DESTRUCTION_METHOD': {
            'display_name': 'Destruction Method',
            'description': 'Methods for secure destruction of records',
            'codes': [
                {'code': 'SECURE_SHRED', 'display_name': 'Secure Shredding', 'description': 'Physical shredding of paper documents', 'sort_order': 1},
                {'code': 'INCINERATION', 'display_name': 'Incineration', 'description': 'Secure incineration of physical materials', 'sort_order': 2},
                {'code': 'DIGITAL_WIPE', 'display_name': 'Digital Wiping', 'description': 'Secure digital overwriting of electronic files', 'sort_order': 3},
                {'code': 'DEGAUSS', 'display_name': 'Degaussing', 'description': 'Magnetic field destruction for magnetic media', 'sort_order': 4},
                {'code': 'PHYSICAL_DESTROY', 'display_name': 'Physical Destruction', 'description': 'Physical destruction of storage media', 'sort_order': 5},
                {'code': 'CERTIFIED_DESTROY', 'display_name': 'Certified Destruction', 'description': 'Third-party certified destruction service', 'sort_order': 6}
            ]
        },
        'CONDITION_TYPE': {
            'display_name': 'Condition Type',
            'description': 'Types of conditions that trigger retention actions',
            'codes': [
                {'code': 'TIME_BASED_RETENTION', 'display_name': 'Time-Based Retention', 'description': 'Retention based on time periods', 'sort_order': 1},
                {'code': 'POST_EVENT_RETENTION', 'display_name': 'Post-Event Retention', 'description': 'Retention based on specific events', 'sort_order': 2},
                {'code': 'FIXED_TERM_RETENTION', 'display_name': 'Fixed-Term Retention', 'description': 'Fixed term retention period', 'sort_order': 3},
                {'code': 'LEGAL_HOLD', 'display_name': 'Legal Hold', 'description': 'Retention due to legal requirements', 'sort_order': 4},
                {'code': 'AUDIT_COMPLETE', 'display_name': 'Audit Completion', 'description': 'Retention until audit completion', 'sort_order': 5},
                {'code': 'PROJECT_END', 'display_name': 'Project End', 'description': 'Retention until project completion', 'sort_order': 6}
            ]
        },
        'CONDITION_EVENT': {
            'display_name': 'Condition Event',
            'description': 'Specific events that can trigger retention conditions',
            'codes': [
                {'code': 'DATE_CREATED', 'display_name': 'Document Creation', 'description': 'Event when document is created', 'sort_order': 1},
                {'code': 'LAST_ACCESS', 'display_name': 'Last Accessed', 'description': 'Event when document is last accessed', 'sort_order': 2},
                {'code': 'APPROVAL', 'display_name': 'Document Approval', 'description': 'Event when document is approved', 'sort_order': 3},
                {'code': 'SIGNATURE', 'display_name': 'Document Signature', 'description': 'Event when document is signed', 'sort_order': 4},
                {'code': 'EXPIRATION', 'display_name': 'Document Expiration', 'description': 'Event when document expires', 'sort_order': 5},
                {'code': 'TERMINATION_DATE', 'display_name': 'Employment Termination', 'description': 'Event when employment ends', 'sort_order': 6},
                {'code': 'CLOSURE', 'display_name': 'Case/Project Closure', 'description': 'Event when case or project closes', 'sort_order': 7}
            ]
        },
        'SERIES': {
            'display_name': 'Document Series',
            'description': 'Document series for organizational classification',
            'codes': [
                {'code': 'FINANCIAL_REPORTS', 'display_name': 'Financial Reports', 'description': 'Financial reporting and accounting documents', 'sort_order': 1},
                {'code': 'HR_RECORDS', 'display_name': 'HR Records', 'description': 'Human resources and personnel documents', 'sort_order': 2},
                {'code': 'LEGAL_CONTRACTS', 'display_name': 'Legal Contracts', 'description': 'Legal contracts and agreements', 'sort_order': 3},
                {'code': 'ADMIN_GENERAL', 'display_name': 'General Administration', 'description': 'General administrative documents', 'sort_order': 4},
                {'code': 'IT_SYSTEMS', 'display_name': 'IT Systems', 'description': 'IT systems and technical documents', 'sort_order': 5},
                {'code': 'OPERATIONS', 'display_name': 'Operations', 'description': 'Operational and procedural documents', 'sort_order': 6},
                {'code': 'PROJECTS', 'display_name': 'Project Management', 'description': 'Project-related documentation', 'sort_order': 7},
                {'code': 'COMPLIANCE', 'display_name': 'Compliance', 'description': 'Regulatory compliance documents', 'sort_order': 8}
            ]
        },
        'CONTAINER_TYPE': {
            'display_name': 'Container Type',
            'description': 'Types of physical containers for document storage',
            'codes': [
                {'code': 'BOX', 'display_name': 'Storage Box', 'description': 'Standard document storage box', 'sort_order': 1},
                {'code': 'FOLDER', 'display_name': 'File Folder', 'description': 'Individual file folder', 'sort_order': 2},
                {'code': 'CABINET', 'display_name': 'File Cabinet', 'description': 'Filing cabinet drawer or section', 'sort_order': 3},
                {'code': 'SHELF', 'display_name': 'Shelf Storage', 'description': 'Open shelf storage system', 'sort_order': 4},
                {'code': 'VAULT', 'display_name': 'Secure Vault', 'description': 'Secure vault storage', 'sort_order': 5},
                {'code': 'DIGITAL', 'display_name': 'Digital Storage', 'description': 'Electronic storage system', 'sort_order': 6}
            ]
        },
        'DISPOSITION_METHOD': {
            'display_name': 'Disposition Method',
            'description': 'Methods for disposing of records after retention period',
            'codes': [
                {'code': 'DESTROY', 'display_name': 'Destroy', 'description': 'Secure destruction of records', 'sort_order': 1},
                {'code': 'TRANSFER_ARCHIVES', 'display_name': 'Transfer to Archives', 'description': 'Transfer to permanent archives', 'sort_order': 2},
                {'code': 'TRANSFER_CUSTODY', 'display_name': 'Transfer Custody', 'description': 'Transfer to another custodian', 'sort_order': 3},
                {'code': 'MIGRATE_FORMAT', 'display_name': 'Migrate Format', 'description': 'Convert to new format for preservation', 'sort_order': 4},
                {'code': 'REVIEW', 'display_name': 'Review for Decision', 'description': 'Review required before disposition', 'sort_order': 5}
            ]
        },
        'LOCATION_TYPE': {
            'display_name': 'Location Type',
            'description': 'Types of storage locations',
            'codes': [
                {'code': 'ONSITE', 'display_name': 'On-Site Storage', 'description': 'Records stored on organizational premises', 'sort_order': 1},
                {'code': 'OFFSITE', 'display_name': 'Off-Site Storage', 'description': 'Records stored at external facility', 'sort_order': 2},
                {'code': 'CLOUD', 'display_name': 'Cloud Storage', 'description': 'Records stored in cloud infrastructure', 'sort_order': 3},
                {'code': 'HYBRID', 'display_name': 'Hybrid Storage', 'description': 'Combination of storage types', 'sort_order': 4}
            ]
        },
        'ACCESS_LEVEL': {
            'display_name': 'Access Level',
            'description': 'Levels of access control for records',
            'codes': [
                {'code': 'OPEN', 'display_name': 'Open Access', 'description': 'Unrestricted access to all staff', 'sort_order': 1},
                {'code': 'RESTRICTED', 'display_name': 'Restricted Access', 'description': 'Access limited to authorized personnel', 'sort_order': 2},
                {'code': 'CONFIDENTIAL', 'display_name': 'Confidential Access', 'description': 'Access limited to specific roles', 'sort_order': 3},
                {'code': 'NEED_TO_KNOW', 'display_name': 'Need-to-Know', 'description': 'Access on need-to-know basis only', 'sort_order': 4}
            ]
        }
    }
    
    return lookup_data

def clear_existing_data(engine):
    """Clear existing data from PDC lookup tables."""
    logger.info("🗑️ Clearing existing data from PDC lookup tables...")
    
    try:
        with engine.begin() as conn:
            # Delete in correct order due to foreign key constraints
            conn.execute(text("DELETE FROM pdc_lookup_codes"))
            conn.execute(text("DELETE FROM pdc_lookup_types"))
            
        logger.info("✅ Existing data cleared successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to clear existing data: {str(e)}")
        return False

def insert_lookup_types(engine, lookup_data):
    """Insert lookup types into pdc_lookup_types table."""
    logger.info("📋 Inserting lookup types...")
    
    try:
        with engine.begin() as conn:
            for lookup_type, type_data in lookup_data.items():
                insert_sql = """
                INSERT INTO pdc_lookup_types (
                    lookup_type, display_name, description, is_active, created_at, created_by
                ) VALUES (
                    :lookup_type, :display_name, :description, :is_active, :created_at, :created_by
                )
                """
                
                conn.execute(text(insert_sql), {
                    'lookup_type': lookup_type,
                    'display_name': type_data['display_name'],
                    'description': type_data['description'],
                    'is_active': True,
                    'created_at': datetime.now(),
                    'created_by': 'synthetic_data_generator'
                })
                
                logger.info(f"  ✅ Inserted lookup type: {lookup_type}")
        
        logger.info(f"✅ Successfully inserted {len(lookup_data)} lookup types")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to insert lookup types: {str(e)}")
        return False

def insert_lookup_codes(engine, lookup_data):
    """Insert lookup codes into pdc_lookup_codes table."""
    logger.info("📋 Inserting lookup codes...")
    
    try:
        total_codes = 0
        with engine.begin() as conn:
            for lookup_type, type_data in lookup_data.items():
                for code_data in type_data['codes']:
                    insert_sql = """
                    INSERT INTO pdc_lookup_codes (
                        lookup_type, lookup_code, display_name, description, 
                        is_active, sort_order, created_at, created_by
                    ) VALUES (
                        :lookup_type, :lookup_code, :display_name, :description,
                        :is_active, :sort_order, :created_at, :created_by
                    )
                    """
                    
                    conn.execute(text(insert_sql), {
                        'lookup_type': lookup_type,
                        'lookup_code': code_data['code'],
                        'display_name': code_data['display_name'],
                        'description': code_data['description'],
                        'is_active': True,
                        'sort_order': code_data['sort_order'],
                        'created_at': datetime.now(),
                        'created_by': 'synthetic_data_generator'
                    })
                    
                    total_codes += 1
                
                logger.info(f"  ✅ Inserted {len(type_data['codes'])} codes for {lookup_type}")
        
        logger.info(f"✅ Successfully inserted {total_codes} lookup codes")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to insert lookup codes: {str(e)}")
        return False

def verify_data_insertion(engine):
    """Verify the data was inserted correctly."""
    logger.info("🔍 Verifying data insertion...")
    
    try:
        with engine.connect() as conn:
            # Count lookup types
            types_result = conn.execute(text("SELECT COUNT(*) as count FROM pdc_lookup_types"))
            types_count = types_result.fetchone()[0]
            
            # Count lookup codes
            codes_result = conn.execute(text("SELECT COUNT(*) as count FROM pdc_lookup_codes"))
            codes_count = codes_result.fetchone()[0]
            
            # Get sample data
            sample_types = conn.execute(text("SELECT lookup_type, display_name FROM pdc_lookup_types ORDER BY lookup_type")).fetchall()
            sample_codes = conn.execute(text("""
                SELECT lookup_type, lookup_code, display_name 
                FROM pdc_lookup_codes 
                ORDER BY lookup_type, sort_order
                OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY
            """)).fetchall()
            
            logger.info(f"📊 Total lookup types: {types_count}")
            logger.info(f"📊 Total lookup codes: {codes_count}")
            
            logger.info("📋 Sample lookup types:")
            for row in sample_types[:5]:
                logger.info(f"  - {row[0]}: {row[1]}")
            
            logger.info("📋 Sample lookup codes:")
            for row in sample_codes:
                logger.info(f"  - {row[0]} > {row[1]}: {row[2]}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        return False

def main():
    """Main function to populate lookup tables with synthetic data."""
    logger.info("🚀 Starting PDC Lookup Tables Data Generation")
    logger.info("=" * 80)
    
    try:
        # Get database engine
        engine = get_engine()
        
        # Get comprehensive lookup data
        lookup_data = get_comprehensive_lookup_data()
        logger.info(f"📋 Prepared {len(lookup_data)} lookup types with synthetic data")
        
        # Clear existing data
        if not clear_existing_data(engine):
            logger.error("❌ Failed to clear existing data. Exiting.")
            return False
        
        # Insert lookup types
        if not insert_lookup_types(engine, lookup_data):
            logger.error("❌ Failed to insert lookup types. Exiting.")
            return False
        
        # Insert lookup codes
        if not insert_lookup_codes(engine, lookup_data):
            logger.error("❌ Failed to insert lookup codes. Exiting.")
            return False
        
        # Verify data insertion
        if not verify_data_insertion(engine):
            logger.error("❌ Data verification failed.")
            return False
        
        logger.info("🎉 Synthetic data generation completed successfully!")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)