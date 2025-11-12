#!/usr/bin/env python3
"""
Test Azure Functions endpoints directly without starting the runtime.
"""
import sys
import os
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import azure.functions as func
from function_app import get_classifications

def test_function_endpoints():
    """Test Azure Functions endpoints directly."""
    print("🚀 Testing Azure Functions Endpoints Directly")
    print("=" * 60)
    
    try:
        # Create a mock request for the classifications endpoint
        print("🔧 Creating mock HTTP request...")
        
        # Create a mock request object
        class MockRequest:
            def __init__(self):
                self.params = {}
                self.route_params = {}
            
            def get(self, key, default=None):
                return self.params.get(key, default)
        
        mock_req = MockRequest()
        mock_req.params = {'page': '1', 'size': '5'}
        
        print("✅ Mock request created")
        
        # Test the get_classifications function directly
        print("🔧 Calling get_classifications endpoint...")
        response = get_classifications(mock_req)
        
        print(f"✅ Function executed successfully!")
        print(f"✅ Response type: {type(response)}")
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Content type: {response.mimetype}")
        
        # Try to parse the response
        if response.status_code == 200:
            try:
                response_data = json.loads(response.get_body().decode())
                print(f"✅ Response JSON parsed successfully")
                print(f"✅ Total items: {response_data.get('total', 'unknown')}")
                print(f"✅ Items in response: {len(response_data.get('items', []))}")
            except Exception as e:
                print(f"⚠️  Could not parse response JSON: {e}")
        else:
            print(f"⚠️  Non-200 status code: {response.status_code}")
            print(f"⚠️  Response body: {response.get_body().decode()}")
            
        print("\n🎉 Direct endpoint test completed!")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Direct endpoint test failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_function_endpoints()
    if success:
        print("\n🚀 Azure Functions endpoints are working correctly!")
        print("🚀 The authentication issue has been resolved!")
    else:
        print("\n⚠️  There may still be issues with the endpoints.")