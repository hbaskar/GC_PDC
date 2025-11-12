"""
Test script for PDC Lookup Service Operations

This script demonstrates all CRUD operations for the PDC lookup tables
using the new simplified service pattern.
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db
from services.lookup_service import PDCLookupService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_lookup_service_operations():
    """Test all CRUD operations for PDC lookup tables using service pattern"""
    
    print("=" * 80)
    print("🚀 PDC Lookup Service Operations Test")
    print("=" * 80)
    
    # Initialize service with database session
    db = next(get_db())
    service = PDCLookupService(db)
    
    try:
        
        # ========== Test Lookup Types ==========
        print("\n📋 Testing Lookup Types Operations")
        print("-" * 50)
        
        # 1. Create new lookup type
        print("1. Creating new lookup type...")
        try:
            from schemas.lookup_schemas import PDCLookupTypeCreate
            
            lookup_type_data = PDCLookupTypeCreate(
                lookup_type="TEST_TYPE",
                display_name="Test Type",
                description="A test lookup type for demonstration",
                created_by="test_script"
            )
            lookup_type = service.create_lookup_type(lookup_type_data)
            print(f"   ✅ Created: {lookup_type.display_name}")
        except Exception as e:
            print(f"   ❌ Failed to create lookup type: {e}")
            return
        
        # 2. Get specific lookup type
        print("2. Getting specific lookup type...")
        retrieved_type = service.get_lookup_type("TEST_TYPE")
        if retrieved_type:
            print(f"   ✅ Found: {retrieved_type.display_name}")
        else:
            print("   ❌ Lookup type not found")
        
        # 3. Get all lookup types
        print("3. Getting all lookup types...")
        all_types = service.get_all_lookup_types()
        print(f"   ✅ Found {len(all_types)} lookup types")
        for lt in all_types[:3]:  # Show first 3
            print(f"      • {lt.lookup_type}: {lt.display_name}")
        if len(all_types) > 3:
            print(f"      ... and {len(all_types) - 3} more")
        
        # 4. Update lookup type
        print("4. Updating lookup type...")
        updated_type = service.update_lookup_type(
            lookup_type="TEST_TYPE",
            display_name="Updated Test Type",
            description="Updated description for test lookup type",
            modified_by="test_script"
        )
        if updated_type:
            print(f"   ✅ Updated: {updated_type.display_name}")
        else:
            print("   ❌ Failed to update lookup type")

        # ========== Test Lookup Codes ==========
        print("\n📋 Testing Lookup Codes Operations")
        print("-" * 50)
        
        # 1. Create new lookup codes
        print("1. Creating new lookup codes...")
        test_codes = [
            {"code": "TEST_CODE_1", "name": "Test Code 1", "description": "First test code", "order": 1},
            {"code": "TEST_CODE_2", "name": "Test Code 2", "description": "Second test code", "order": 2}
        ]
        
        for code_data in test_codes:
            try:
                from schemas.lookup_schemas import PDCLookupCodeCreate
                
                lookup_code_data = PDCLookupCodeCreate(
                    lookup_type="TEST_TYPE",
                    lookup_code=code_data["code"],
                    display_name=code_data["name"],
                    description=code_data["description"],
                    sort_order=code_data["order"],
                    created_by="test_script"
                )
                lookup_code = service.create_lookup_code(lookup_code_data)
                print(f"   ✅ Created: {lookup_code.display_name}")
            except Exception as e:
                print(f"   ❌ Failed to create lookup code {code_data['code']}: {e}")
        
        # 2. Get specific lookup code
        print("2. Getting specific lookup code...")
        retrieved_code = service.get_lookup_code("TEST_TYPE", "TEST_CODE_1")
        if retrieved_code:
            print(f"   ✅ Found: {retrieved_code.display_name}")
        else:
            print("   ❌ Lookup code not found")
        
        # 3. Get codes by type
        print("3. Getting codes by type...")
        codes_by_type = service.get_lookup_codes_by_type("TEST_TYPE")
        print(f"   ✅ Found {len(codes_by_type)} codes for TEST_TYPE")
        for code in codes_by_type:
            print(f"      • {code.lookup_code}: {code.display_name}")
        
        # 4. Update lookup code
        print("4. Updating lookup code...")
        updated_code = service.update_lookup_code(
            lookup_type="TEST_TYPE",
            lookup_code="TEST_CODE_1",
            display_name="Updated Test Code 1",
            description="Updated description for test code",
            modified_by="test_script"
        )
        if updated_code:
            print(f"   ✅ Updated: {updated_code.display_name}")
        else:
            print("   ❌ Failed to update lookup code")

        # ========== Test Utility Operations ==========
        print("\n📋 Testing Utility Operations")
        print("-" * 50)
        
        # 1. Search for codes containing 'PUBLIC'
        print("1. Searching for codes containing 'PUBLIC'...")
        search_results = service.search_lookup_codes('PUBLIC', limit=5)
        if search_results:
            print(f"   Found {len(search_results)} results:")
            for result in search_results:
                print(f"      • {result.lookup_type}.{result.lookup_code}: {result.display_name}")
        else:
            print("   No results found")
        
        # 2. Get lookup statistics
        print("2. Getting lookup statistics...")
        stats = service.get_lookup_stats()
        print(f"   ✅ Lookup Types: {stats['lookup_types']['active']} active, {stats['lookup_types']['total']} total")
        print(f"   ✅ Lookup Codes: {stats['lookup_codes']['active']} active, {stats['lookup_codes']['total']} total")
        
        # 3. Get lookup hierarchy sample
        print("3. Getting lookup hierarchy sample...")
        hierarchy = service.get_lookup_hierarchy()
        print(f"   Retrieved hierarchy for {len(hierarchy)} lookup types:")
        for lookup_type, codes in list(hierarchy.items())[:3]:  # Show first 3 types
            print(f"      • {lookup_type}: {len(codes)} codes")
        if len(hierarchy) > 3:
            print(f"      ... and {len(hierarchy) - 3} more types")

        # ========== Cleanup Test Data ==========
        print("\n📋 Cleaning up test data...")
        print("-" * 50)
        
        # 1. Delete test lookup codes
        print("1. Deleting test lookup codes...")
        for code_data in test_codes:
            deleted = service.delete_lookup_code("TEST_TYPE", code_data["code"])
            if deleted:
                print(f"   ✅ Deleted {code_data['code']}")
            else:
                print(f"   ❌ Failed to delete {code_data['code']}")
        
        # 2. Delete test lookup type
        print("2. Deleting test lookup type...")
        deleted = service.delete_lookup_type("TEST_TYPE")
        if deleted:
            print("   ✅ Deleted TEST_TYPE")
        else:
            print("   ❌ Failed to delete TEST_TYPE")

        print("\n🎉 PDC Lookup Service operations test completed successfully!")

        # ========== Demonstrate Real Data Operations ==========
        print("\n" + "=" * 80)
        print("🔍 Demonstrating Real Data Operations")
        print("=" * 80)
        
        # Show classification levels
        print("📋 Classification Levels:")
        classification_codes = service.get_lookup_codes_by_type("CLASSIFICATION_LEVEL")
        for code in classification_codes:
            print(f"   • {code.lookup_code}: {code.display_name}")
        
        # Show media types  
        print("\n📋 Media Types:")
        media_codes = service.get_lookup_codes_by_type("MEDIA_TYPE")
        for code in media_codes:
            print(f"   • {code.lookup_code}: {code.display_name}")
        
        # Show file types
        print("\n📋 File Types:")
        file_codes = service.get_lookup_codes_by_type("FILE_TYPE")
        for code in file_codes:
            print(f"   • {code.lookup_code}: {code.display_name}")
        
        # Search demonstration
        print("\n🔍 Search for 'ELECTRONIC' in all types:")
        electronic_results = service.search_lookup_codes('ELECTRONIC', limit=5)
        for result in electronic_results:
            print(f"   • {result.lookup_type}.{result.lookup_code}: {result.display_name}")

        print("\n✅ All tests completed successfully!")
    
    finally:
        # Close database session
        db.close()

def main():
    """Main function to run the test"""
    try:
        test_lookup_service_operations()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()