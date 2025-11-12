#!/usr/bin/env python3
"""
Test the diagnostic endpoint locally.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import azure.functions as func
from function_app import diagnostic_check

def test_diagnostic_endpoint():
    """Test the diagnostic endpoint locally."""
    print("🔍 Testing Diagnostic Endpoint")
    print("=" * 60)
    
    # Set environment to managed identity for testing
    original_auth_method = os.environ.get('AZURE_SQL_AUTH_METHOD')
    os.environ['AZURE_SQL_AUTH_METHOD'] = 'managed_identity'
    
    try:
        # Create a mock request
        class MockRequest:
            def __init__(self):
                self.params = {}
                self.route_params = {}
        
        mock_req = MockRequest()
        
        print("🔧 Calling diagnostic endpoint...")
        response = diagnostic_check(mock_req)
        
        print(f"✅ Response status: {response.status_code}")
        print(f"✅ Response type: {response.mimetype}")
        
        if response.status_code == 200:
            import json
            diagnostic_data = json.loads(response.get_body().decode())
            
            print("\n📋 Diagnostic Results:")
            print("=" * 40)
            
            print("Environment Variables:")
            for key, value in diagnostic_data.get("environment_variables", {}).items():
                print(f"  {key}: {value}")
            
            print("\nDatabase Config:")
            db_config = diagnostic_data.get("database_config", {})
            if isinstance(db_config, dict):
                for key, value in db_config.items():
                    if key == "connection_string":
                        print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  ERROR: {db_config}")
            
            print("\nEngine Info:")
            engine_info = diagnostic_data.get("engine_info", {})
            if isinstance(engine_info, dict):
                for key, value in engine_info.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  ERROR: {engine_info}")
                
        else:
            print(f"❌ Error response: {response.get_body().decode()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    finally:
        # Restore original auth method
        if original_auth_method:
            os.environ['AZURE_SQL_AUTH_METHOD'] = original_auth_method
        else:
            os.environ.pop('AZURE_SQL_AUTH_METHOD', None)

if __name__ == "__main__":
    success = test_diagnostic_endpoint()
    if success:
        print("\n🚀 Diagnostic endpoint is working!")
        print("🚀 Deploy this to Azure and call /api/diagnostic to see what's happening in the cloud.")
    else:
        print("\n⚠️  Diagnostic endpoint has issues.")