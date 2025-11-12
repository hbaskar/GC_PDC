"""
Authentication method testing script.
Tests both SQL authentication and Managed Identity configuration.
"""
import sys
from pathlib import Path
import os

# Add the project root to Python path (go up one level from scripts/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.config import DatabaseConfig

def test_sql_auth_config():
    """Test SQL authentication configuration."""
    print("🔐 Testing SQL Authentication Configuration")
    print("=" * 60)
    
    try:
        # Temporarily set SQL auth environment variables
        original_auth_method = os.environ.get('AZURE_SQL_AUTH_METHOD')
        os.environ['AZURE_SQL_AUTH_METHOD'] = 'sql'
        
        # Create new config instance
        config = DatabaseConfig()
        
        print(f"✅ Auth Method: {config.auth_method}")
        print(f"✅ Server: {config.server}")
        print(f"✅ Database: {config.database}")
        print(f"✅ Username: {config.username}")
        print(f"✅ Authentication: {config.authentication}")
        
        # Test connection string generation (but don't connect)
        if config.username and config.password:
            conn_str = config.get_connection_string()
            print("✅ Connection string generated successfully")
            print(f"✅ Connection method: SQL Authentication")
        else:
            print("⚠️  Missing username or password for SQL authentication")
            print("   Set AZURE_SQL_USERNAME and AZURE_SQL_PASSWORD in .env")
        
        # Restore original auth method
        if original_auth_method:
            os.environ['AZURE_SQL_AUTH_METHOD'] = original_auth_method
        else:
            os.environ.pop('AZURE_SQL_AUTH_METHOD', None)
            
        return True
        
    except Exception as e:
        print(f"❌ SQL Authentication test failed: {e}")
        return False

def test_managed_identity_config():
    """Test Managed Identity configuration."""
    print("\n🔐 Testing Managed Identity Configuration")
    print("=" * 60)
    
    try:
        # Temporarily set Managed Identity environment variables
        original_auth_method = os.environ.get('AZURE_SQL_AUTH_METHOD')
        original_client_id = os.environ.get('AZURE_CLIENT_ID')
        
        os.environ['AZURE_SQL_AUTH_METHOD'] = 'managed_identity'
        
        # Test System-Assigned Managed Identity
        print("\n📋 System-Assigned Managed Identity:")
        os.environ.pop('AZURE_CLIENT_ID', None)
        
        config = DatabaseConfig()
        print(f"✅ Auth Method: {config.auth_method}")
        print(f"✅ Server: {config.server}")
        print(f"✅ Database: {config.database}")
        print(f"✅ Client ID: {config.managed_identity_client_id or 'None (System-Assigned)'}")
        
        if config.server and config.database:
            conn_str = config.get_connection_string()
            print("✅ Connection string generated successfully")
            print(f"✅ Connection method: System-Assigned Managed Identity")
        else:
            print("⚠️  Missing server or database for Managed Identity")
            print("   Set AZURE_SQL_SERVER and AZURE_SQL_DATABASE in .env")
        
        # Test User-Assigned Managed Identity
        print("\n📋 User-Assigned Managed Identity:")
        test_client_id = "12345678-1234-1234-1234-123456789012"
        os.environ['AZURE_CLIENT_ID'] = test_client_id
        
        config = DatabaseConfig()
        print(f"✅ Auth Method: {config.auth_method}")
        print(f"✅ Client ID: {config.managed_identity_client_id}")
        
        if config.server and config.database:
            conn_str = config.get_connection_string()
            print("✅ Connection string generated successfully")
            print(f"✅ Connection method: User-Assigned Managed Identity")
        
        # Restore original environment variables
        if original_auth_method:
            os.environ['AZURE_SQL_AUTH_METHOD'] = original_auth_method
        else:
            os.environ.pop('AZURE_SQL_AUTH_METHOD', None)
            
        if original_client_id:
            os.environ['AZURE_CLIENT_ID'] = original_client_id
        else:
            os.environ.pop('AZURE_CLIENT_ID', None)
            
        return True
        
    except Exception as e:
        print(f"❌ Managed Identity test failed: {e}")
        return False

def test_invalid_auth_method():
    """Test invalid authentication method handling."""
    print("\n🔐 Testing Invalid Authentication Method")
    print("=" * 60)
    
    try:
        # Temporarily set invalid auth method
        original_auth_method = os.environ.get('AZURE_SQL_AUTH_METHOD')
        os.environ['AZURE_SQL_AUTH_METHOD'] = 'invalid_method'
        
        config = DatabaseConfig()
        
        # This should raise a ValueError
        try:
            conn_str = config.get_connection_string()
            print("❌ Invalid auth method was accepted (this should not happen)")
            return False
        except ValueError as ve:
            print(f"✅ Invalid auth method correctly rejected: {ve}")
        
        # Restore original auth method
        if original_auth_method:
            os.environ['AZURE_SQL_AUTH_METHOD'] = original_auth_method
        else:
            os.environ.pop('AZURE_SQL_AUTH_METHOD', None)
            
        return True
        
    except Exception as e:
        print(f"❌ Invalid auth method test failed: {e}")
        return False

def show_current_config():
    """Show current configuration from environment."""
    print("\n🔧 Current Environment Configuration")
    print("=" * 60)
    
    config = DatabaseConfig()
    
    print(f"Auth Method: {config.auth_method}")
    print(f"Server: {config.server}")
    print(f"Database: {config.database}")
    
    if config.auth_method == 'sql':
        print(f"Username: {config.username}")
        print(f"Password: {'***' if config.password else 'Not Set'}")
        print(f"Authentication: {config.authentication}")
    elif config.auth_method == 'managed_identity':
        print(f"Managed Identity Type: {'User-Assigned' if config.managed_identity_client_id else 'System-Assigned'}")
        if config.managed_identity_client_id:
            print(f"Client ID: {config.managed_identity_client_id}")
    
    print(f"Driver: {config.driver}")
    print(f"Port: {config.port}")
    
    try:
        conn_str = config.get_connection_string()
        print("✅ Connection string can be generated")
    except Exception as e:
        print(f"❌ Connection string generation failed: {e}")

def main():
    """Main test function."""
    print("🚀 PDC Classification Authentication Testing")
    print("=" * 60)
    
    success = True
    
    # Show current configuration
    show_current_config()
    
    # Test SQL Authentication
    if not test_sql_auth_config():
        success = False
    
    # Test Managed Identity
    if not test_managed_identity_config():
        success = False
    
    # Test Invalid Authentication Method
    if not test_invalid_auth_method():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All authentication tests passed!")
        print("\n📋 Configuration Summary:")
        print("  ✅ SQL Authentication: Supported")
        print("  ✅ System-Assigned Managed Identity: Supported")
        print("  ✅ User-Assigned Managed Identity: Supported")
        print("  ✅ Invalid Method Handling: Working")
        print("\n💡 Usage:")
        print("  - For local development: Use AZURE_SQL_AUTH_METHOD=sql")
        print("  - For Azure production: Use AZURE_SQL_AUTH_METHOD=managed_identity")
        print("  - Configure environment variables in .env file")
    else:
        print("❌ Some authentication tests failed")

if __name__ == "__main__":
    main()