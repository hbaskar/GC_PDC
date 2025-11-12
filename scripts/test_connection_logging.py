#!/usr/bin/env python3
"""
Test the connection creation with logging to see what's happening.
"""
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_connection_with_logging():
    """Test connection creation with detailed logging."""
    print("🔍 Testing Connection Creation with Logging")
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
        
        print("🔧 Environment set to managed_identity")
        
        # Import and trigger engine creation
        from database.config import get_engine
        
        print("🔧 Creating engine (this should show logging)...")
        engine = get_engine()
        
        print("✅ Engine created successfully!")
        
        # Try to actually create a connection (this will fail but show the connection string)
        print("🔧 Attempting connection (this will show ODBC connection string in logs)...")
        try:
            with engine.connect() as conn:
                print("✅ Connection successful!")
        except Exception as e:
            print(f"⚠️  Connection failed (expected for MI locally): {str(e)[:100]}...")
        
        return True
        
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
    test_connection_with_logging()