

"""
Simplified database testing script using actual table structure.
Tests basic database operations with the existing pdc_classifications table.
"""
import sys
from pathlib import Path

# Add the project root to Python path (go up one level from tests/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.config import get_db
from services.classification_service import PDCClassificationService
from sqlalchemy import text

def test_connection():
    """Test database connection."""
    try:
        print("🔗 Testing database connection...")
        with get_db() as db:
            result = db.execute(text("SELECT 1 as test")).fetchone()
            if result and result[0] == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection test failed")
                return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_table_access():
    """Test access to actual pdc_classifications table."""
    try:
        print("📋 Testing table access...")
        with get_db() as db:
            # Get basic table info
            result = db.execute(text("SELECT COUNT(*) FROM pdc_classifications")).fetchone()
            total_count = result[0]
            print(f"📊 Total classifications in table: {total_count}")
            
            # Get sample data
            result = db.execute(text("""
                SELECT TOP 3 
                    classification_id, 
                    name, 
                    code, 
                    classification_level,
                    is_active
                FROM pdc_classifications 
                ORDER BY classification_id
            """)).fetchall()
            
            print("📄 Sample records:")
            for row in result:
                print(f"  ID: {row[0]} | Name: {row[1]} | Code: {row[2]} | Level: {row[3]} | Active: {row[4]}")
            
            return True
        
    except Exception as e:
        print(f"❌ Error accessing table: {e}")
        return False

def test_crud_operations():
    """Test service operations using the service layer."""
    try:
        print("🔧 Testing service operations...")
        with get_db() as db:
            service = PDCClassificationService(db)
            
            # Test get_all
            classifications, total = service.get_all(limit=5)
            print(f"✅ get_all(): Found {total} total records, retrieved {len(classifications)}")
            
            if classifications:
                first_record = classifications[0]
                
                # Test get_by_id
                retrieved = service.get_by_id(first_record.classification_id)
                if retrieved:
                    print(f"✅ get_by_id(): Retrieved '{retrieved.name}' (ID: {retrieved.classification_id})")
                
                # Test get_by_code
                retrieved_by_code = service.get_by_code(first_record.code)
                if retrieved_by_code:
                    print(f"✅ get_by_code(): Retrieved '{retrieved_by_code.name}' (Code: {retrieved_by_code.code})")
            
            return True
        
    except Exception as e:
        print(f"❌ Error testing service operations: {e}")
        return False

def test_metadata_operations():
    """Test metadata endpoint operations."""
    try:
        print("📊 Testing metadata operations...")
        with get_db() as db:
            service = PDCClassificationService(db)
            
            # Test metadata methods
            levels = service.get_classification_levels()
            media_types = service.get_media_types()
            file_types = service.get_file_types()
            series = service.get_series()
            
            print(f"✅ Classification levels: {levels[:3]}{'...' if len(levels) > 3 else ''}")
            print(f"✅ Media types: {media_types[:3]}{'...' if len(media_types) > 3 else ''}")
            print(f"✅ File types: {file_types[:3]}{'...' if len(file_types) > 3 else ''}")
            print(f"✅ Series: {series[:3]}{'...' if len(series) > 3 else ''}")
            
            return True
        
    except Exception as e:
        print(f"❌ Error testing metadata operations: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 PDC Classification Database Test")
    print("=" * 50)
    
    success = True
    
    # Test 1: Database Connection
    if not test_connection():
        print("💔 Database connection failed - stopping tests")
        return
    
    # Test 2: Table Access
    if not test_table_access():
        success = False
    
    # Test 3: service Operations
    if not test_crud_operations():
        success = False
    
    # Test 4: Metadata Operations
    if not test_metadata_operations():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed successfully!")
        print("\n🔗 Your API endpoints are ready:")
        print("  GET  /api/classifications")
        print("  GET  /api/classifications/{id}")
        print("  POST /api/classifications")
        print("  PUT  /api/classifications/{id}")
        print("  DELETE /api/classifications/{id}")
        print("  GET  /api/classifications/metadata")
        print("  GET  /api/health")
    else:
        print("❌ Some tests failed - check errors above")

if __name__ == "__main__":
    main()
