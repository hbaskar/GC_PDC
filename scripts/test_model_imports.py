"""
Test script to verify all models import correctly after reorganization.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_model_imports():
    """Test that all models can be imported successfully."""
    
    print("🧪 Testing Model Imports After Reorganization")
    print("=" * 60)
    
    try:
        # Test Base import
        print("1. Testing Base import...")
        from models.base import Base
        print("   ✅ Base imported successfully")
        
        # Test individual model imports
        print("\n2. Testing individual model imports...")
        
        from models.pdc_lookup_type import PDCLookupType
        print("   ✅ PDCLookupType imported successfully")
        
        from models.pdc_lookup_code import PDCLookupCode
        print("   ✅ PDCLookupCode imported successfully")
        
        from models.pdc_classification import PDCClassification
        print("   ✅ PDCClassification imported successfully")
        
        from models.pdc_retention_policy import PDCRetentionPolicy
        print("   ✅ PDCRetentionPolicy imported successfully")
        
        from models.pdc_template import PDCTemplate
        print("   ✅ PDCTemplate imported successfully")
        
        from models.pdc_template_field import PDCTemplateField
        print("   ✅ PDCTemplateField imported successfully")
        
        from models.pdc_organization import PDCOrganization
        print("   ✅ PDCOrganization imported successfully")
        
        # Test package-level imports
        print("\n3. Testing package-level imports...")
        
        from models import (
            Base, PDCLookupType, PDCLookupCode, PDCClassification,
            PDCRetentionPolicy, PDCTemplate, PDCTemplateField, PDCOrganization
        )
        print("   ✅ All models imported from package successfully")
        
        # Test model instantiation (without database connection)
        print("\n4. Testing model class inspection...")
        
        print(f"   • PDCLookupType table: {PDCLookupType.__tablename__}")
        print(f"   • PDCLookupCode table: {PDCLookupCode.__tablename__}")
        print(f"   • PDCClassification table: {PDCClassification.__tablename__}")
        print(f"   • PDCRetentionPolicy table: {PDCRetentionPolicy.__tablename__}")
        print(f"   • PDCTemplate table: {PDCTemplate.__tablename__}")
        print(f"   • PDCTemplateField table: {PDCTemplateField.__tablename__}")
        print(f"   • PDCOrganization table: {PDCOrganization.__tablename__}")
        
        # Test service import
        print("\n5. Testing service operations...")
        from services.lookup_service import PDCLookupService
        print(f"   ✅ Service class imported: {PDCLookupService.__name__}")
        
        print("\n🎉 All model imports successful!")
        print("📋 Model Organization Summary:")
        print("   • 7 domain models in separate files")
        print("   • 1 base configuration file")
        print("   • 1 service class for lookup operations")
        print("   • 1 package __init__.py file")
        print("   • All imports working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_model_imports()
    if success:
        print("\n✅ Model reorganization completed successfully!")
    else:
        print("\n❌ Model reorganization has issues that need to be fixed.")
        sys.exit(1)