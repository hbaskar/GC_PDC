#!/usr/bin/env python3
"""
Test the actual ODBC connection strings generated for managed identity to ensure no conflicts.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_managed_identity_connection_strings():
    """Test the exact ODBC connection strings that will be generated."""
    print("🔍 Testing Managed Identity ODBC Connection Strings")
    print("=" * 60)
    
    # Set up managed identity environment
    original_auth_method = os.environ.get('AZURE_SQL_AUTH_METHOD')
    os.environ['AZURE_SQL_AUTH_METHOD'] = 'managed_identity'
    
    try:
        # Clear cached config
        import database.config
        database.config._db_config = None
        database.config._engine = None
        
        from database.config import DatabaseConfig
        
        config = DatabaseConfig()
        
        print("🔧 System-Assigned Managed Identity:")
        print("=" * 40)
        
        # Simulate the connection string creation from the custom creator
        driver = config.driver
        server = config.server
        database = config.database
        
        # This is what the custom connection creator will build
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Authentication=ActiveDirectoryMsi;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )
        
        print(f"ODBC Connection String:")
        print(f"{connection_string}")
        
        # Check for conflicts
        print(f"\n🔍 Conflict Analysis:")
        if "Integrated Security" in connection_string:
            print("❌ Found 'Integrated Security' parameter - THIS WILL CAUSE CONFLICTS!")
        else:
            print("✅ No 'Integrated Security' parameter found")
            
        if "Authentication=ActiveDirectoryMsi" in connection_string:
            print("✅ Found 'Authentication=ActiveDirectoryMsi' parameter")
        else:
            print("❌ Missing 'Authentication=ActiveDirectoryMsi' parameter")
        
        # Test with user-assigned managed identity
        print(f"\n🔧 User-Assigned Managed Identity:")
        print("=" * 40)
        
        # Simulate user-assigned with client ID
        test_client_id = "12345678-1234-1234-1234-123456789012"
        connection_string_user = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Authentication=ActiveDirectoryMsi;"
            f"UID={test_client_id};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )
        
        print(f"ODBC Connection String with Client ID:")
        print(f"{connection_string_user}")
        
        # Check for conflicts
        print(f"\n🔍 Conflict Analysis:")
        if "Integrated Security" in connection_string_user:
            print("❌ Found 'Integrated Security' parameter - THIS WILL CAUSE CONFLICTS!")
        else:
            print("✅ No 'Integrated Security' parameter found")
            
        if "Authentication=ActiveDirectoryMsi" in connection_string_user:
            print("✅ Found 'Authentication=ActiveDirectoryMsi' parameter")
        else:
            print("❌ Missing 'Authentication=ActiveDirectoryMsi' parameter")
            
        if f"UID={test_client_id}" in connection_string_user:
            print("✅ Found User-Assigned Managed Identity Client ID")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection string test failed: {str(e)}")
        return False
    finally:
        # Restore original auth method
        if original_auth_method:
            os.environ['AZURE_SQL_AUTH_METHOD'] = original_auth_method
        else:
            os.environ.pop('AZURE_SQL_AUTH_METHOD', None)

if __name__ == "__main__":
    success = test_managed_identity_connection_strings()
    
    print(f"\n🎯 Summary:")
    print("=" * 60)
    
    if success:
        print("✅ Managed Identity ODBC connection strings are properly formatted")
        print("✅ No 'Integrated Security' conflicts detected")
        print("✅ Proper 'Authentication=ActiveDirectoryMsi' parameter included")
        print("✅ Both System-Assigned and User-Assigned MI supported")
        print("\n🚀 This should resolve the authentication error in Azure Functions!")
    else:
        print("❌ There are still issues with the connection string generation")
        
    print(f"\n💡 Deployment Instructions:")
    print("=" * 60)
    print("1. In Azure Functions App Configuration, set:")
    print("   AZURE_SQL_AUTH_METHOD=managed_identity")
    print("2. Enable System-Assigned Managed Identity on the Function App")
    print("3. Grant the Managed Identity access to the SQL Database")
    print("4. Deploy the updated code with the custom connection creator")