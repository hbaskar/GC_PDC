#!/usr/bin/env python3
"""
Test direct pyodbc connection to isolate the issue.
"""
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pyodbc_direct():
    """Test direct pyodbc connection."""
    print("🔍 Direct pyodbc Connection Test")
    print("=" * 60)
    
    # Test 1: ActiveDirectoryPassword
    print("\n1️⃣ Testing ActiveDirectoryPassword:")
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=ggndadev-sqlsvr01.database.windows.net;"
        "DATABASE=CMSDEVDB;"
        "Authentication=ActiveDirectoryPassword;"
        "UID=hari.baskarus@gavelguardai.com;"
        f"PWD={os.getenv('AZURE_SQL_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    
    try:
        conn = pyodbc.connect(connection_string)
        print("✅ ActiveDirectoryPassword connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ ActiveDirectoryPassword failed: {e}")
    
    # Test 2: SQL Server Authentication (no Authentication parameter)
    print("\n2️⃣ Testing SQL Server Authentication:")
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=ggndadev-sqlsvr01.database.windows.net;"
        "DATABASE=CMSDEVDB;"
        "UID=hari.baskarus@gavelguardai.com;"
        f"PWD={os.getenv('AZURE_SQL_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    
    try:
        conn = pyodbc.connect(connection_string)
        print("✅ SQL Server Authentication connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ SQL Server Authentication failed: {e}")
    
    # Test 3: ActiveDirectoryIntegrated 
    print("\n3️⃣ Testing ActiveDirectoryIntegrated:")
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=ggndadev-sqlsvr01.database.windows.net;"
        "DATABASE=CMSDEVDB;"
        "Authentication=ActiveDirectoryIntegrated;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    
    try:
        conn = pyodbc.connect(connection_string)
        print("✅ ActiveDirectoryIntegrated connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ ActiveDirectoryIntegrated failed: {e}")

if __name__ == "__main__":
    test_pyodbc_direct()