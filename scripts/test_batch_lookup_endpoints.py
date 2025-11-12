"""
Test script for the new batch lookup codes endpoints.
Demonstrates both POST and GET methods for retrieving multiple lookup types at once.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db
from services.lookup_service import PDCLookupService
import json

def simulate_batch_endpoints():
    """Simulate the new batch endpoints with real data."""
    print("🧪 Testing Batch Lookup Codes Endpoints")
    print("=" * 60)
    
    # Get database connection and service
    db = next(get_db())
    service = PDCLookupService(db)
    
    try:
        # Test 1: Simulate POST /lookups/batch/codes
        print("\n1. Simulating POST /lookups/batch/codes...")
        
        # Sample request body
        request_body = {
            "lookup_types": ["CLASSIFICATION_LEVEL", "MEDIA_TYPE", "FILE_TYPE"],
            "active_only": True,
            "include_inactive_types": False
        }
        
        result = {
            "lookup_types": [],
            "requested_count": len(request_body["lookup_types"]),
            "found_count": 0,
            "not_found": [],
            "total_codes": 0
        }
        
        for lookup_type in request_body["lookup_types"]:
            # Verify lookup type exists
            db_lookup_type = service.get_lookup_type(lookup_type)
            if not db_lookup_type:
                result["not_found"].append(lookup_type)
                continue
                
            # Get codes for this type
            codes = service.get_lookup_codes_by_type(
                lookup_type, 
                active_only=request_body["active_only"]
            )
            
            # Build type response
            type_response = {
                "lookup_type": lookup_type,
                "display_name": db_lookup_type.display_name,
                "description": db_lookup_type.description,
                "is_active": db_lookup_type.is_active,
                "codes": [code.to_dict() for code in codes],
                "code_count": len(codes)
            }
            
            result["lookup_types"].append(type_response)
            result["total_codes"] += len(codes)
        
        result["found_count"] = len(result["lookup_types"])
        
        print(f"   ✅ Requested: {result['requested_count']} types")
        print(f"   ✅ Found: {result['found_count']} types")
        print(f"   ✅ Total codes: {result['total_codes']}")
        print(f"   ✅ Not found: {result['not_found']}")
        
        for type_data in result["lookup_types"]:
            print(f"      • {type_data['lookup_type']}: {type_data['code_count']} codes")
        
        # Test 2: Simulate GET /lookups/batch/codes with query params
        print("\n2. Simulating GET /lookups/batch/codes?types=CLASSIFICATION_LEVEL,CONDITION_EVENT...")
        
        query_types = ["CLASSIFICATION_LEVEL", "CONDITION_EVENT"]
        
        result2 = {
            "lookup_types": [],
            "requested_count": len(query_types),
            "found_count": 0,
            "not_found": [],
            "total_codes": 0
        }
        
        for lookup_type in query_types:
            db_lookup_type = service.get_lookup_type(lookup_type)
            if not db_lookup_type:
                result2["not_found"].append(lookup_type)
                continue
            
            codes = service.get_lookup_codes_by_type(lookup_type, active_only=True)
            
            type_response = {
                "lookup_type": lookup_type,
                "display_name": db_lookup_type.display_name,
                "description": db_lookup_type.description,
                "is_active": db_lookup_type.is_active,
                "codes": [code.to_dict() for code in codes],
                "code_count": len(codes)
            }
            
            result2["lookup_types"].append(type_response)
            result2["total_codes"] += len(codes)
        
        result2["found_count"] = len(result2["lookup_types"])
        
        print(f"   ✅ Query method - Found: {result2['found_count']} types")
        print(f"   ✅ Total codes: {result2['total_codes']}")
        
        for type_data in result2["lookup_types"]:
            print(f"      • {type_data['lookup_type']}: {type_data['code_count']} codes")
            # Show first few codes as example
            for i, code in enumerate(type_data['codes'][:3]):
                print(f"        - {code['lookup_code']}: {code['display_name']}")
            if len(type_data['codes']) > 3:
                print(f"        ... and {len(type_data['codes']) - 3} more")
        
        # Test 3: Error cases
        print("\n3. Testing error cases...")
        
        # Non-existent lookup type
        error_types = ["CLASSIFICATION_LEVEL", "NONEXISTENT_TYPE", "MEDIA_TYPE"]
        
        error_result = {
            "lookup_types": [],
            "requested_count": len(error_types),
            "found_count": 0,
            "not_found": [],
            "total_codes": 0
        }
        
        for lookup_type in error_types:
            db_lookup_type = service.get_lookup_type(lookup_type)
            if not db_lookup_type:
                error_result["not_found"].append(lookup_type)
                continue
            
            codes = service.get_lookup_codes_by_type(lookup_type, active_only=True)
            type_response = {
                "lookup_type": lookup_type,
                "display_name": db_lookup_type.display_name,
                "code_count": len(codes)
            }
            
            error_result["lookup_types"].append(type_response)
            error_result["total_codes"] += len(codes)
        
        error_result["found_count"] = len(error_result["lookup_types"])
        
        print(f"   ✅ Error handling - Requested: {error_result['requested_count']}")
        print(f"   ✅ Found: {error_result['found_count']}")
        print(f"   ✅ Not found: {error_result['not_found']}")
        
        # Test 4: JSON response size estimate
        print("\n4. Testing response size...")
        
        json_size = len(json.dumps(result, default=str))
        print(f"   ✅ Sample response size: {json_size:,} characters")
        print(f"   ✅ Estimated payload size: ~{json_size/1024:.1f} KB")
        
        print("\n🎉 All batch endpoint simulations completed successfully!")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    simulate_batch_endpoints()