#!/usr/bin/env python3
"""
Test that the lazy initialization resolves the authentication issue by simulating an API call.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.config import get_db
from services.pdc_service import PDCClassificationCRUD

def test_lazy_database_initialization():
    """Test that lazy initialization works without authentication conflicts."""
    print("🔍 Testing Lazy Database Initialization")
    print("=" * 60)
    
    try:
        # This should trigger the lazy initialization of the engine
        print("🔧 Calling get_db() to trigger lazy initialization...")
        db = next(get_db())
        
        print("✅ Database session created successfully!")
        
        # Try to create the CRUD service (this uses the database)
        print("🔧 Creating PDC Classification CRUD service...")
        crud = PDCClassificationCRUD(db)
        
        print("✅ CRUD service created successfully!")
        
        # Try a simple database operation
        print("🔧 Testing simple database query...")
        # Just test that we can execute a basic query - get first few records
        classifications, total = crud.get_all(skip=0, limit=1)
        print(f"✅ Database query successful! Total records: {total}")
        
        print("\n🎉 All lazy initialization tests passed!")
        print("✅ No authentication conflicts detected!")
        return True
        
    except Exception as e:
        print(f"❌ Lazy initialization test failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    success = test_lazy_database_initialization()
    if success:
        print("\n🚀 The authentication issue should be resolved!")
        print("🚀 Azure Functions runtime should now work correctly.")
    else:
        print("\n⚠️  There may still be authentication issues.")