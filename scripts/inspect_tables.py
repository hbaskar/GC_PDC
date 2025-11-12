"""
Script to inspect existing table structure from CMSDEVB database
and generate SQLAlchemy models based on actual table definitions.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path (go up one level from scripts/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.config import get_engine
import sqlalchemy as sa
from sqlalchemy import inspect, text

def get_table_info(table_name):
    """Get detailed information about a table."""
    engine = get_engine()
    inspector = inspect(engine)
    
    try:
        # Check if table exists
        if not inspector.has_table(table_name):
            print(f"❌ Table '{table_name}' does not exist in the database")
            return None
        
        print(f"📋 Table: {table_name}")
        print("=" * 50)
        
        # Get columns information
        columns = inspector.get_columns(table_name)
        print("🔧 Columns:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            autoincrement = " IDENTITY" if col.get('autoincrement') else ""
            
            print(f"  - {col['name']}: {col['type']}{autoincrement} {nullable}{default}")
        
        # Get primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint['constrained_columns']:
            print(f"\n🔑 Primary Key: {', '.join(pk_constraint['constrained_columns'])}")
        
        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print(f"\n🔗 Foreign Keys:")
            for fk in foreign_keys:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print(f"\n📊 Indexes:")
            for idx in indexes:
                unique = "UNIQUE " if idx['unique'] else ""
                print(f"  - {unique}{idx['name']}: {', '.join(idx['column_names'])}")
        
        # Get unique constraints
        unique_constraints = inspector.get_unique_constraints(table_name)
        if unique_constraints:
            print(f"\n🚫 Unique Constraints:")
            for uc in unique_constraints:
                print(f"  - {uc['name']}: {', '.join(uc['column_names'])}")
        
        print("\n" + "=" * 50)
        return columns
        
    except Exception as e:
        print(f"❌ Error inspecting table '{table_name}': {e}")
        return None

def find_pdc_tables():
    """Find all tables related to PDC (Product Data Classification)."""
    engine = get_engine()
    inspector = inspect(engine)
    
    try:
        all_tables = inspector.get_table_names()
        
        # Look for tables with 'pdc' or 'classification' in the name
        pdc_tables = []
        for table in all_tables:
            if 'pdc' in table.lower() or 'classification' in table.lower():
                pdc_tables.append(table)
        
        print("🔍 Found PDC-related tables:")
        for table in pdc_tables:
            print(f"  - {table}")
        
        return pdc_tables
        
    except Exception as e:
        print(f"❌ Error finding PDC tables: {e}")
        return []

def generate_sqlalchemy_model(table_name, columns):
    """Generate SQLAlchemy model code based on table structure."""
    if not columns:
        return None
    
    # Map SQL Server types to SQLAlchemy types
    type_mapping = {
        'INTEGER': 'Integer',
        'BIGINT': 'BigInteger',
        'SMALLINT': 'SmallInteger',
        'TINYINT': 'SmallInteger',
        'BIT': 'Boolean',
        'NVARCHAR': 'String',
        'VARCHAR': 'String',
        'NCHAR': 'String',
        'CHAR': 'String',
        'NTEXT': 'Text',
        'TEXT': 'Text',
        'DATETIME2': 'DateTime',
        'DATETIME': 'DateTime',
        'DATE': 'Date',
        'TIME': 'Time',
        'DECIMAL': 'Numeric',
        'FLOAT': 'Float',
        'REAL': 'Float',
        'MONEY': 'Numeric',
        'UNIQUEIDENTIFIER': 'String'
    }
    
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    
    model_code = f'''"""
SQLAlchemy model for {table_name} table.
Auto-generated from database schema.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, BigInteger, SmallInteger, Date, Time, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class {class_name}(Base):
    """Model for {table_name} table."""
    __tablename__ = "{table_name}"
    
'''
    
    # Generate column definitions
    for col in columns:
        col_name = col['name']
        col_type_str = str(col['type'])
        
        # Extract base type
        base_type = col_type_str.split('(')[0].upper()
        
        # Map to SQLAlchemy type
        if base_type in type_mapping:
            sa_type = type_mapping[base_type]
        else:
            sa_type = 'String'  # Default fallback
        
        # Handle type parameters
        if 'VARCHAR' in base_type or 'NVARCHAR' in base_type or 'CHAR' in base_type or 'NCHAR' in base_type:
            if '(' in col_type_str and ')' in col_type_str:
                length = col_type_str.split('(')[1].split(')')[0]
                if length != 'max':
                    sa_type = f"String({length})"
            else:
                sa_type = "Text"
        
        # Column definition parts
        col_parts = [f'Column({sa_type}']
        
        # Primary key
        if col.get('autoincrement') or col_name.lower() == 'id':
            col_parts.append('primary_key=True')
        
        # Nullable
        if not col['nullable']:
            col_parts.append('nullable=False')
        
        # Default value
        if col['default']:
            default_val = col['default']
            if 'getdate()' in str(default_val).lower() or 'now()' in str(default_val).lower():
                col_parts.append('server_default=func.now()')
            else:
                col_parts.append(f"default={repr(default_val)}")
        
        # Index hint for common searchable fields
        if col_name.lower() in ['name', 'code', 'category', 'status', 'type']:
            col_parts.append('index=True')
        
        col_definition = f"    {col_name} = {', '.join(col_parts)})"
        model_code += col_definition + '\n'
    
    # Add __repr__ method
    model_code += f'''
    def __repr__(self):
        return f"<{class_name}(id={{self.id if hasattr(self, 'id') else 'N/A'}})>"
'''
    
    return model_code

def main():
    """Main function to inspect tables and generate models."""
    print("🚀 Database Table Inspector for PDC Classification System")
    print("=" * 60)
    
    try:
        # Test connection
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Find PDC tables
        pdc_tables = find_pdc_tables()
        
        if not pdc_tables:
            print("❌ No PDC-related tables found. Checking for 'pdc_classifications' specifically...")
            # Try the specific table name
            columns = get_table_info('pdc_classifications')
            if columns:
                print("\n🎯 Generating SQLAlchemy model for pdc_classifications:")
                model_code = generate_sqlalchemy_model('pdc_classifications', columns)
                if model_code:
                    print(model_code)
        else:
            # Inspect each found table
            for table_name in pdc_tables:
                columns = get_table_info(table_name)
                if columns:
                    print(f"\n🎯 Generated SQLAlchemy model for {table_name}:")
                    model_code = generate_sqlalchemy_model(table_name, columns)
                    if model_code:
                        print(model_code)
                        print("\n" + "-" * 60)
        
        # Also check for related tables that might exist
        related_tables = ['classifications', 'categories', 'sub_classifications']
        print(f"\n🔍 Checking for related tables...")
        for table_name in related_tables:
            columns = get_table_info(table_name)
            if columns:
                print(f"\n🎯 Generated SQLAlchemy model for {table_name}:")
                model_code = generate_sqlalchemy_model(table_name, columns)
                if model_code:
                    print(model_code)
                    print("\n" + "-" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()