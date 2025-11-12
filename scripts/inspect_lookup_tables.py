#!/usr/bin/env python3
"""
Inspect lookup_types and lookup_codes table structures and create synthetic data.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.config import get_engine
from sqlalchemy import inspect, text
import json

def inspect_lookup_tables():
    """Inspect the structure of lookup_types and lookup_codes tables."""
    print("🔍 Inspecting Lookup Tables Structure")
    print("=" * 60)
    
    try:
        engine = get_engine()
        inspector = inspect(engine)
        
        # Check if tables exist
        tables = inspector.get_table_names()
        lookup_tables = [t for t in tables if 'lookup' in t.lower()]
        
        print(f"📋 Found lookup tables: {lookup_tables}")
        
        for table_name in lookup_tables:
            print(f"\n🔍 Table: {table_name}")
            print("-" * 40)
            
            # Get column information
            columns = inspector.get_columns(table_name)
            print("📋 Columns:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f"DEFAULT: {col['default']}" if col['default'] else ""
                print(f"  - {col['name']}: {col['type']} {nullable} {default}")
            
            # Get primary keys
            pk = inspector.get_pk_constraint(table_name)
            if pk['constrained_columns']:
                print(f"🔑 Primary Key: {pk['constrained_columns']}")
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print("🔗 Foreign Keys:")
                for fk in fks:
                    print(f"  - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
            
            # Get sample data if any exists
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                count = result.fetchone()[0]
                print(f"📊 Current record count: {count}")
                
                if count > 0:
                    result = conn.execute(text(f"SELECT TOP 3 * FROM {table_name}"))
                    rows = result.fetchall()
                    column_names = result.keys()
                    print("📋 Sample data:")
                    for i, row in enumerate(rows, 1):
                        print(f"  Row {i}: {dict(zip(column_names, row))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Inspection failed: {str(e)}")
        return False

def get_metadata_from_classifications():
    """Get unique values from pdc_classifications that should be in lookup tables."""
    print("\n🔍 Extracting Metadata from Classifications")
    print("=" * 60)
    
    try:
        engine = get_engine()
        
        metadata_queries = {
            'classification_levels': "SELECT DISTINCT classification_level FROM pdc_classifications WHERE classification_level IS NOT NULL",
            'media_types': "SELECT DISTINCT media_type FROM pdc_classifications WHERE media_type IS NOT NULL",
            'file_types': "SELECT DISTINCT file_type FROM pdc_classifications WHERE file_type IS NOT NULL",
            'series': "SELECT DISTINCT series FROM pdc_classifications WHERE series IS NOT NULL",
            'destruction_methods': "SELECT DISTINCT destruction_method FROM pdc_classifications WHERE destruction_method IS NOT NULL",
            'condition_types': "SELECT DISTINCT condition_type FROM pdc_classifications WHERE condition_type IS NOT NULL",
            'condition_events': "SELECT DISTINCT condition_event FROM pdc_classifications WHERE condition_event IS NOT NULL"
        }
        
        metadata = {}
        
        with engine.connect() as conn:
            for category, query in metadata_queries.items():
                try:
                    result = conn.execute(text(query))
                    values = [row[0] for row in result.fetchall() if row[0]]
                    metadata[category] = values
                    print(f"📋 {category}: {values}")
                except Exception as e:
                    print(f"❌ Failed to get {category}: {e}")
                    metadata[category] = []
        
        return metadata
        
    except Exception as e:
        print(f"❌ Metadata extraction failed: {str(e)}")
        return {}

def create_synthetic_lookup_data():
    """Create comprehensive synthetic data for lookup tables."""
    print("\n🔍 Creating Synthetic Lookup Data")
    print("=" * 60)
    
    # Define lookup types and their corresponding codes
    lookup_data = {
        'classification_level': {
            'description': 'Classification security levels for documents and records',
            'codes': [
                {'code': 'PUBLIC', 'name': 'Public', 'description': 'Information that can be freely shared'},
                {'code': 'INTERNAL', 'name': 'Internal Use', 'description': 'Information for internal organizational use only'},
                {'code': 'CONFIDENTIAL', 'name': 'Confidential', 'description': 'Sensitive information requiring protection'},
                {'code': 'RESTRICTED', 'name': 'Restricted', 'description': 'Highly sensitive information with limited access'},
                {'code': 'SECRET', 'name': 'Secret', 'description': 'Top secret information requiring highest security'}
            ]
        },
        'media_type': {
            'description': 'Types of media formats for storing information',
            'codes': [
                {'code': 'PAPER', 'name': 'Paper Documents', 'description': 'Physical paper-based documents'},
                {'code': 'ELECTRONIC', 'name': 'Electronic Files', 'description': 'Digital files and documents'},
                {'code': 'MICROFILM', 'name': 'Microfilm', 'description': 'Microfilm storage medium'},
                {'code': 'MICROFICHE', 'name': 'Microfiche', 'description': 'Microfiche storage cards'},
                {'code': 'OPTICAL', 'name': 'Optical Media', 'description': 'CD, DVD, and other optical storage'},
                {'code': 'MAGNETIC', 'name': 'Magnetic Media', 'description': 'Magnetic tape and disk storage'},
                {'code': 'HYBRID', 'name': 'Hybrid Format', 'description': 'Combination of multiple media types'}
            ]
        },
        'file_type': {
            'description': 'Categories of file types and document formats',
            'codes': [
                {'code': 'ADMIN', 'name': 'Administrative', 'description': 'Administrative and operational documents'},
                {'code': 'LEGAL', 'name': 'Legal Documents', 'description': 'Legal contracts, agreements, and compliance'},
                {'code': 'FINANCIAL', 'name': 'Financial Records', 'description': 'Financial statements, invoices, and accounting'},
                {'code': 'HR', 'name': 'Human Resources', 'description': 'Employee records and HR documentation'},
                {'code': 'TECHNICAL', 'name': 'Technical Documentation', 'description': 'Technical specifications and manuals'},
                {'code': 'CORRESPONDENCE', 'name': 'Correspondence', 'description': 'Letters, emails, and communications'},
                {'code': 'REPORTS', 'name': 'Reports', 'description': 'Business reports and analytics'},
                {'code': 'POLICIES', 'name': 'Policies & Procedures', 'description': 'Organizational policies and procedures'}
            ]
        },
        'destruction_method': {
            'description': 'Methods for secure destruction of records',
            'codes': [
                {'code': 'SHRED', 'name': 'Shredding', 'description': 'Physical shredding of paper documents'},
                {'code': 'INCINERATE', 'name': 'Incineration', 'description': 'Secure incineration of physical materials'},
                {'code': 'DEGAUSS', 'name': 'Degaussing', 'description': 'Magnetic field destruction for magnetic media'},
                {'code': 'OVERWRITE', 'name': 'Digital Overwrite', 'description': 'Secure digital overwriting of electronic files'},
                {'code': 'PHYSICAL_DESTROY', 'name': 'Physical Destruction', 'description': 'Physical destruction of storage media'},
                {'code': 'CERTIFIED_DESTROY', 'name': 'Certified Destruction', 'description': 'Third-party certified destruction service'}
            ]
        },
        'condition_type': {
            'description': 'Types of conditions that trigger retention actions',
            'codes': [
                {'code': 'TIME_BASED', 'name': 'Time-Based', 'description': 'Retention based on time periods'},
                {'code': 'EVENT_BASED', 'name': 'Event-Based', 'description': 'Retention based on specific events'},
                {'code': 'LEGAL_HOLD', 'name': 'Legal Hold', 'description': 'Retention due to legal requirements'},
                {'code': 'AUDIT_COMPLETE', 'name': 'Audit Completion', 'description': 'Retention until audit completion'},
                {'code': 'PROJECT_END', 'name': 'Project End', 'description': 'Retention until project completion'},
                {'code': 'CONTRACT_END', 'name': 'Contract End', 'description': 'Retention until contract expiration'}
            ]
        },
        'condition_event': {
            'description': 'Specific events that can trigger retention conditions',
            'codes': [
                {'code': 'CREATION', 'name': 'Document Creation', 'description': 'Event when document is created'},
                {'code': 'LAST_ACCESS', 'name': 'Last Accessed', 'description': 'Event when document is last accessed'},
                {'code': 'APPROVAL', 'name': 'Document Approval', 'description': 'Event when document is approved'},
                {'code': 'SIGNATURE', 'name': 'Document Signature', 'description': 'Event when document is signed'},
                {'code': 'EXPIRATION', 'name': 'Document Expiration', 'description': 'Event when document expires'},
                {'code': 'TERMINATION', 'name': 'Employment Termination', 'description': 'Event when employment ends'},
                {'code': 'CLOSURE', 'name': 'Case/Project Closure', 'description': 'Event when case or project closes'}
            ]
        },
        'series': {
            'description': 'Document series for organizational classification',
            'codes': [
                {'code': 'ADMIN-001', 'name': 'General Administration', 'description': 'General administrative documents'},
                {'code': 'LEGAL-001', 'name': 'Legal Affairs', 'description': 'Legal department documents'},
                {'code': 'FIN-001', 'name': 'Financial Management', 'description': 'Financial and accounting documents'},
                {'code': 'HR-001', 'name': 'Human Resources Management', 'description': 'HR and personnel documents'},
                {'code': 'IT-001', 'name': 'Information Technology', 'description': 'IT systems and technical documents'},
                {'code': 'OPS-001', 'name': 'Operations', 'description': 'Operational and procedural documents'},
                {'code': 'PROJ-001', 'name': 'Project Management', 'description': 'Project-related documentation'},
                {'code': 'COMP-001', 'name': 'Compliance', 'description': 'Regulatory compliance documents'}
            ]
        },
        'sensitivity_rating': {
            'description': 'Numerical sensitivity ratings for information classification',
            'codes': [
                {'code': '1', 'name': 'Minimal Sensitivity', 'description': 'Low sensitivity information'},
                {'code': '2', 'name': 'Low Sensitivity', 'description': 'Slightly sensitive information'},
                {'code': '3', 'name': 'Moderate Sensitivity', 'description': 'Moderately sensitive information'},
                {'code': '4', 'name': 'High Sensitivity', 'description': 'Highly sensitive information'},
                {'code': '5', 'name': 'Maximum Sensitivity', 'description': 'Extremely sensitive information'}
            ]
        },
        'organization_type': {
            'description': 'Types of organizations in the system',
            'codes': [
                {'code': 'DEPT', 'name': 'Department', 'description': 'Organizational department'},
                {'code': 'DIV', 'name': 'Division', 'description': 'Organizational division'},
                {'code': 'UNIT', 'name': 'Business Unit', 'description': 'Business unit or team'},
                {'code': 'BRANCH', 'name': 'Branch Office', 'description': 'Branch or regional office'},
                {'code': 'SUBSIDIARY', 'name': 'Subsidiary', 'description': 'Subsidiary organization'},
                {'code': 'VENDOR', 'name': 'Vendor/Contractor', 'description': 'External vendor or contractor'}
            ]
        }
    }
    
    return lookup_data

if __name__ == "__main__":
    print("🚀 Lookup Tables Analysis and Data Generation")
    print("=" * 80)
    
    # Step 1: Inspect existing table structures
    if inspect_lookup_tables():
        print("\n✅ Table inspection completed")
    
    # Step 2: Extract existing metadata from classifications
    existing_metadata = get_metadata_from_classifications()
    
    # Step 3: Create synthetic lookup data
    synthetic_data = create_synthetic_lookup_data()
    
    print(f"\n📋 Generated synthetic data for {len(synthetic_data)} lookup types")
    print("📋 Available lookup types:")
    for lookup_type, info in synthetic_data.items():
        print(f"  - {lookup_type}: {len(info['codes'])} codes")
    
    print(f"\n💾 Synthetic data structure created successfully!")
    print("🚀 Next step: Create insertion script to populate the tables")