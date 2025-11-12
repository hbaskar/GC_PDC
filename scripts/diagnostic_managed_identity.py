#!/usr/bin/env python3
"""
Comprehensive diagnostic to check managed identity configuration step by step.
"""
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def diagnostic_check():
    """Run comprehensive diagnostic of managed identity configuration."""
    print("🔍 Comprehensive Managed Identity Diagnostic")
    print("=" * 60)
    
    # Set environment to managed identity
    original_auth_method = os.environ.get('AZURE_SQL_AUTH_METHOD')
    os.environ['AZURE_SQL_AUTH_METHOD'] = 'managed_identity'
    
    try:
        # Clear any cached database configuration
        import database.config
        database.config._engine = None
        database.config._SessionLocal = None
        database.config._db_config = None
        
        print("🔧 Step 1: Environment Variables")
        print(f"   AZURE_SQL_AUTH_METHOD: {os.environ.get('AZURE_SQL_AUTH_METHOD')}")
        print(f"   AZURE_SQL_SERVER: {os.environ.get('AZURE_SQL_SERVER')}")
        print(f"   AZURE_SQL_DATABASE: {os.environ.get('AZURE_SQL_DATABASE')}")
        
        print("\n🔧 Step 2: Database Configuration Creation")
        from database.config import DatabaseConfig
        
        config = DatabaseConfig()
        print(f"   auth_method: {config.auth_method}")
        print(f"   server: {config.server}")
        print(f"   database: {config.database}")
        print(f"   driver: {config.driver}")
        print(f"   managed_identity_client_id: {config.managed_identity_client_id}")
        
        print("\n🔧 Step 3: Engine Creation Condition Check")
        sql_condition = (config.auth_method == 'sql' and getattr(config, 'authentication', None) == 'ActiveDirectoryPassword')
        mi_condition = (config.auth_method == 'managed_identity')
        combined_condition = sql_condition or mi_condition
        
        print(f"   SQL condition (sql + ActiveDirectoryPassword): {sql_condition}")
        print(f"   MI condition (managed_identity): {mi_condition}")
        print(f"   Combined condition (should be True): {combined_condition}")
        
        if combined_condition:
            print("   ✅ Will use custom connection creator")
        else:
            print("   ❌ Will use standard SQLAlchemy connection - THIS IS THE PROBLEM!")
        
        print("\n🔧 Step 4: Connection String Generation")
        connection_string = config.get_connection_string()
        print(f"   Generated connection string: {connection_string}")
        
        # Check for problematic parameters in the connection string
        print("\n🔧 Step 5: Connection String Analysis")
        if "Integrated%20Security" in connection_string or "Integrated+Security" in connection_string:
            print("   ❌ Found URL-encoded 'Integrated Security' in connection string!")
        elif "Integrated Security" in connection_string:
            print("   ❌ Found 'Integrated Security' in connection string!")
        else:
            print("   ✅ No 'Integrated Security' found in connection string")
            
        if "Authentication=ActiveDirectoryMsi" in connection_string:
            print("   ✅ Found 'Authentication=ActiveDirectoryMsi' in connection string")
        else:
            print("   ❌ Missing 'Authentication=ActiveDirectoryMsi' in connection string")
        
        print("\n🔧 Step 6: Engine Creation")
        from database.config import get_engine
        
        engine = get_engine()
        print(f"   Engine created: {type(engine)}")
        
        if hasattr(engine.pool, '_creator'):
            print("   ✅ Custom connection creator is set")
        else:
            print("   ❌ No custom connection creator - using standard SQLAlchemy!")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original auth method
        if original_auth_method:
            os.environ['AZURE_SQL_AUTH_METHOD'] = original_auth_method
        else:
            os.environ.pop('AZURE_SQL_AUTH_METHOD', None)

if __name__ == "__main__":
    diagnostic_check()