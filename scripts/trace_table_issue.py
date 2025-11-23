
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect
from models import Base, PDCLibrary, PDCClassification
from database.config import get_engine

# Update this connection string to match your environment
DATABASE_URL = "sqlite:///your_database.db"  # or your actual connection string

engine = get_engine()
inspector = inspect(engine)

print("Tables in SQLAlchemy metadata:")
print(Base.metadata.tables.keys())

print("\nTables in the database:")
print(inspector.get_table_names())

print("\npdc_libraries columns:")
for col in inspector.get_columns('pdc_libraries'):
    print(f"  {col['name']} ({col['type']})")

print("\npdc_classifications columns:")
for col in inspector.get_columns('pdc_classifications'):
    print(f"  {col['name']} ({col['type']})")

print("\npdc_classifications foreign keys:")
for fk in inspector.get_foreign_keys('pdc_classifications'):
    print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

print("\nDone tracing table and foreign key setup.")