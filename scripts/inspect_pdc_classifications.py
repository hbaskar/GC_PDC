"""
Inspect the pdc_classifications table structure and generate appropriate models.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path (go up one level from scripts/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.config import get_engine
from sqlalchemy import inspect, text

def inspect_pdc_classifications():
    """Get detailed information about pdc_classifications table."""
    engine = get_engine()
    inspector = inspect(engine)
    
    try:
        # Get column information
        columns = inspector.get_columns('pdc_classifications')
        
        print("📋 pdc_classifications Table Structure:")
        print("=" * 60)
        
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            autoincrement = " IDENTITY" if col.get('autoincrement') else ""
            
            print(f"  - {col['name']}: {col['type']}{autoincrement} {nullable}{default}")
        
        # Get primary keys
        pk_constraint = inspector.get_pk_constraint('pdc_classifications')
        if pk_constraint['constrained_columns']:
            print(f"\n🔑 Primary Key: {', '.join(pk_constraint['constrained_columns'])}")
        
        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys('pdc_classifications')
        if foreign_keys:
            print(f"\n🔗 Foreign Keys:")
            for fk in foreign_keys:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Get sample data
        print(f"\n📊 Sample Data:")
        # Reuse engine from earlier in function
        with engine.connect() as conn:
            result = conn.execute(text("SELECT TOP 5 * FROM pdc_classifications"))
            rows = result.fetchall()
            column_names = result.keys()
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"Row {i}: {dict(zip(column_names, row))}")
            else:
                print("  (No data found)")
        
        return columns
        
    except Exception as e:
        print(f"❌ Error inspecting pdc_classifications table: {e}")
        return None

def generate_model_from_actual_table(columns):
    """Generate SQLAlchemy model based on actual table structure."""
    if not columns:
        return None
    
    type_mapping = {
        'INTEGER': 'Integer',
        'BIGINT': 'BigInteger',
        'SMALLINT': 'SmallInteger',
        'BIT': 'Boolean',
        'NVARCHAR': 'String',
        'VARCHAR': 'String',
        'NTEXT': 'Text',
        'TEXT': 'Text',
        'DATETIME2': 'DateTime',
        'DATETIME': 'DateTime',
        'DECIMAL': 'Numeric',
        'FLOAT': 'Float'
    }
    
    model_code = '''"""
SQLAlchemy models for PDC (Product Data Classification) system.
Based on actual database table structure from CMSDEVB.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, BigInteger, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class PDCClassification(Base):
    """Model for pdc_classifications table."""
    __tablename__ = "pdc_classifications"
    
'''
    
    for col in columns:
        col_name = col['name']
        col_type_str = str(col['type'])
        
        # Extract base type
        base_type = col_type_str.split('(')[0].upper()
        
        # Map to SQLAlchemy type
        if base_type in type_mapping:
            sa_type = type_mapping[base_type]
        else:
            sa_type = 'String'
        
        # Handle type parameters for strings
        if 'VARCHAR' in base_type or 'NVARCHAR' in base_type:
            if '(' in col_type_str and ')' in col_type_str:
                length = col_type_str.split('(')[1].split(')')[0]
                if length != 'max':
                    sa_type = f"String({length})"
                else:
                    sa_type = "Text"
            else:
                sa_type = "Text"
        
        # Column definition parts
        col_parts = [f'Column({sa_type}']
        
        # Primary key
        if col.get('autoincrement') or 'id' in col_name.lower():
            col_parts.append('primary_key=True')
        
        # Nullable
        if not col['nullable']:
            col_parts.append('nullable=False')
        
        # Default value
        if col['default']:
            default_val = str(col['default']).lower()
            if 'getdate()' in default_val or 'now()' in default_val:
                col_parts.append('server_default=func.now()')
            elif default_val == '((1))':
                col_parts.append('default=True')
            elif default_val == '((0))':
                col_parts.append('default=False')
            else:
                col_parts.append(f"server_default=text('{col['default']}')")
        
        # Index hint for common searchable fields
        if col_name.lower() in ['name', 'code', 'category', 'status', 'type', 'classification_name', 'classification_code']:
            col_parts.append('index=True')
        
        col_definition = f"    {col_name} = {', '.join(col_parts)})"
        model_code += col_definition + '\n'
    
    model_code += '''
    def __repr__(self):
        id_field = getattr(self, 'classification_id', getattr(self, 'id', 'N/A'))
        name_field = getattr(self, 'classification_name', getattr(self, 'name', 'N/A'))
        return f"<PDCClassification(id={id_field}, name='{name_field}')>"
'''
    
    return model_code

def main():
    """Main function to inspect and generate model."""
    print("🔍 Inspecting pdc_classifications Table Structure")
    print("=" * 60)
    
    columns = inspect_pdc_classifications()
    
    if columns:
        print(f"\n🎯 Generated SQLAlchemy Model:")
        print("=" * 60)
        
        model_code = generate_model_from_actual_table(columns)
        if model_code:
            print(model_code)

if __name__ == "__main__":
    main()