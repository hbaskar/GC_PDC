#!/usr/bin/env python3
"""
Test script to validate blueprint functionality without starting the full function host
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_blueprint_imports():
    """Test that all blueprints can be imported successfully"""
    try:
        print("Testing blueprint imports...")
        
        # Test classifications blueprint
        from blueprints.classifications import bp as classifications_bp
        print("✅ Classifications blueprint imported successfully")
        
        # Test lookups blueprint  
        from blueprints.lookups import bp as lookups_bp
        print("✅ Lookups blueprint imported successfully")
        
        # Test health blueprint
        from blueprints.health import bp as health_bp
        print("✅ Health blueprint imported successfully")
        
        # Test main function app
        import function_app
        print("✅ Main function app imported successfully")
        
        print("\n🎉 All blueprint imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint import failed: {str(e)}")
        return False

def test_service_methods():
    """Test that all required service methods exist"""
    try:
        print("\nTesting service methods...")
        
        from services.pdc_service import PDCClassificationCRUD
        from database.config import get_db
        
        # Get a database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        # Test method existence
        required_methods = ['get_all', 'get_by_id', 'create', 'update', 'soft_delete', 'restore']
        
        for method_name in required_methods:
            if hasattr(crud, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
                return False
        
        print("🎉 All required service methods exist!")
        return True
        
    except Exception as e:
        print(f"❌ Service method test failed: {str(e)}")
        return False

def test_schema_imports():
    """Test that all schemas can be imported"""
    try:
        print("\nTesting schema imports...")
        
        # Test classification schemas
        from schemas.pdc_schemas import (
            PDCClassificationCreate,
            PDCClassificationUpdate, 
            PDCClassificationResponse
        )
        print("✅ Classification schemas imported")
        
        # Test lookup schemas
        from schemas.lookup_schemas import (
            PDCLookupTypeCreate,
            PDCLookupCodeCreate,
            PDCLookupTypeResponse,
            PDCLookupCodeResponse
        )
        print("✅ Lookup schemas imported")
        
        print("🎉 All schema imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Schema import failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PDC BLUEPRINT VALIDATION TEST")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_blueprint_imports()
    all_passed &= test_service_methods() 
    all_passed &= test_schema_imports()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The application should work correctly.")
    else:
        print("❌ SOME TESTS FAILED! Check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())