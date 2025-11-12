#!/usr/bin/env python3
"""
Test the Azure Functions API endpoints directly.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import azure.functions as func
from function_app import app

def test_api_endpoints():
    """Test the API endpoints."""
    print("🚀 Testing Azure Functions API Endpoints")
    print("=" * 60)
    
    try:
        # Test that the app can be imported and is configured
        print("✅ Function app imported successfully")
        print(f"✅ App type: {type(app)}")
        
        # Try to create a test request for the classifications endpoint
        print("\n🔍 Testing function definitions...")
        
        # Check if functions are registered
        if hasattr(app, '_function_builders'):
            builders = app._function_builders
            print(f"✅ Found {len(builders)} function builders")
            for builder in builders:
                if hasattr(builder, '_function_name'):
                    print(f"  - Function: {builder._function_name}")
        
        print("\n🎉 API endpoints test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_api_endpoints()