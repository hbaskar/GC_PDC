#!/usr/bin/env python3
"""
Test actual database connection with the new authentication setup.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.config import get_engine, get_session_local
from sqlalchemy import text

def test_database_connection():
    """Test the actual database connection."""
    print("🔗 Testing Database Connection")
    print("=" * 60)
    
    try:
        # Test engine connection
        print("🔍 Testing SQLAlchemy engine connection...")
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT @@VERSION as version"))
            version = result.fetchone()
            print(f"✅ Database connection successful!")
            print(f"✅ SQL Server Version: {version[0][:100]}...")
            
        # Test session creation
        print("\n🔍 Testing SessionLocal creation...")
        SessionLocal = get_session_local()
        session = SessionLocal()
        try:
            result = session.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()
            print(f"✅ Session test successful! Result: {test_value[0]}")
        finally:
            session.close()
            
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_database_connection()