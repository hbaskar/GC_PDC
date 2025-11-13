#!/usr/bin/env python3
"""
Debug connection string generation to see what's causing the authentication conflict.
"""
import sys
import os
from urllib.parse import quote_plus

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.config import DatabaseConfig

def debug_connection_strings():
    """Debug what connection strings are being generated."""
    print("🔍 Connection String Debug")
    print("=" * 60)
    
    # Create config instance
    db_config = DatabaseConfig()
    
    print(f"Auth Method: {db_config.auth_method}")
    print(f"Authentication: {db_config.authentication}")
    print(f"Server: {db_config.server}")
    print(f"Database: {db_config.database}")
    print(f"Driver: {db_config.driver}")
    print(f"Username: {db_config.username}")
    
    # Generate connection string
    connection_string = db_config.get_connection_string()
    print(f"\n📋 Generated Connection String:")
    print(f"{connection_string}")
    
    # Parse out individual components
    print(f"\n🔍 Connection String Analysis:")
    if "?" in connection_string:
        base, params = connection_string.split("?", 1)
        print(f"Base URL: {base}")
        print(f"Parameters:")
        for param in params.split("&"):
            print(f"  - {param}")
    
    # Check for conflicts
    print(f"\n⚠️  Checking for Conflicts:")
    if "Integrated" in connection_string:
        print("❌ Found 'Integrated Security' parameter in connection string!")
    if "Authentication=" in connection_string:
        print("✅ Found 'Authentication' parameter in connection string")
    if "UID=" in connection_string:
        print("✅ Found 'UID' parameter in connection string")
    if "PWD=" in connection_string:
        print("✅ Found 'PWD' parameter in connection string")

if __name__ == "__main__":
    debug_connection_strings()
