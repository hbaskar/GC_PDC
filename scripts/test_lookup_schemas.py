"""
Test script to demonstrate the new lookup API endpoints.
This shows how to call the lookup APIs and validates the schema-based responses.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db
from services.lookup_service import PDCLookupService
from schemas.lookup_schemas import PDCLookupTypeResponse, PDCLookupCodeResponse
import json

def test_lookup_schemas():
    """Test the lookup schemas with real data."""
    print("🧪 Testing Lookup Schemas with Real Data")
    print("=" * 60)
    
    # Get database connection and service
    db = next(get_db())
    service = PDCLookupService(db)
    
    try:
        # Test 1: Get lookup types and serialize with schemas
        print("\n1. Testing lookup type schema serialization...")
        lookup_types = service.get_all_lookup_types(active_only=True, skip=0, limit=3)
        
        for lookup_type in lookup_types:
            # Convert using schema
            response_data = PDCLookupTypeResponse.model_validate(lookup_type).model_dump()
            print(f"   ✅ {response_data['lookup_type']}: {response_data['display_name']}")
        
        # Test 2: Get lookup codes and serialize with schemas
        print("\n2. Testing lookup code schema serialization...")
        lookup_codes = service.get_lookup_codes_by_type("CLASSIFICATION_LEVEL", active_only=True, skip=0, limit=3)
        
        for lookup_code in lookup_codes:
            # Convert using schema
            response_data = PDCLookupCodeResponse.model_validate(lookup_code).model_dump()
            print(f"   ✅ {response_data['lookup_code']}: {response_data['display_name']}")
        
        # Test 3: Test pagination methods
        print("\n3. Testing pagination methods...")
        total_types = service.count_lookup_types(active_only=True)
        total_codes = service.count_lookup_codes_by_type("MEDIA_TYPE", active_only=True)
        
        print(f"   ✅ Total lookup types: {total_types}")
        print(f"   ✅ Total MEDIA_TYPE codes: {total_codes}")
        
        # Test 4: Simulate API response format
        print("\n4. Simulating API response format...")
        
        # Simulate GET /lookups/types response
        types_response = {
            "items": [
                PDCLookupTypeResponse.model_validate(lt).model_dump() 
                for lt in service.get_all_lookup_types(active_only=True, skip=0, limit=2)
            ],
            "total": service.count_lookup_types(active_only=True),
            "page": 1,
            "size": 2,
            "pages": (service.count_lookup_types(active_only=True) + 1) // 2
        }
        
        print(f"   ✅ API Response format validated:")
        print(f"      - Items: {len(types_response['items'])}")
        print(f"      - Total: {types_response['total']}")
        print(f"      - Pages: {types_response['pages']}")
        
        # Test 5: JSON serialization
        print("\n5. Testing JSON serialization...")
        json_output = json.dumps(types_response, default=str, indent=2)
        print(f"   ✅ JSON serialization successful ({len(json_output)} chars)")
        
        print("\n🎉 All lookup schema tests passed!")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_lookup_schemas()