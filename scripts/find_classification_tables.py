"""
Script to find and inspect classification-related tables in CMSDEVB database.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path (go up one level from scripts/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.config import get_engine
from sqlalchemy import text

def find_classification_tables():
    """Find all tables that might contain classification data."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                AND TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """))
            
            all_tables = [row[0] for row in result.fetchall()]
            print(f"📋 Found {len(all_tables)} tables in total")
            
            # Look for tables containing specific keywords
            keywords = ['classification', 'category', 'type', 'class', 'metadata', 'data_class']
            relevant_tables = []
            
            for table in all_tables:
                table_lower = table.lower()
                for keyword in keywords:
                    if keyword in table_lower:
                        relevant_tables.append(table)
                        break
            
            print("\n🎯 Tables that might contain classification data:")
            for table in relevant_tables:
                print(f"  - {table}")
            
            # Also show all PDC tables
            pdc_tables = [table for table in all_tables if 'pdc' in table.lower()]
            print(f"\n📊 All PDC-related tables:")
            for table in pdc_tables:
                print(f"  - {table}")
            
            return pdc_tables + relevant_tables
            
    except Exception as e:
        print(f"❌ Error finding tables: {e}")
        return []

def inspect_table_content(table_name, limit=5):
    """Get sample data from a table to understand its structure."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT TOP {limit} * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
            
            print(f"\n📊 Sample data from {table_name}:")
            print("Columns:", list(columns))
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"Row {i}: {dict(zip(columns, row))}")
            else:
                print("  (No data found)")
                
    except Exception as e:
        print(f"❌ Error inspecting {table_name}: {e}")

def main():
    """Main function to find and inspect classification tables."""
    print("🔍 Finding Classification Tables in CMSDEVB")
    print("=" * 50)
    
    tables = find_classification_tables()
    
    # Inspect a few key tables
    key_tables = ['pdc_templates', 'pdc_template_fields', 'pdc_retention_policies']
    
    for table in key_tables:
        if table in tables:
            inspect_table_content(table, 3)

if __name__ == "__main__":
    main()
