# Tests Directory

This directory contains test scripts and utilities for testing the PDC Classifications API functionality.

## Test Files

### `test_db.py`
**Purpose**: Comprehensive database and API testing script
- Tests database connectivity and configuration
- Validates CRUD operations through service layer
- Tests metadata endpoints and functionality
- Provides health check and validation

**Usage**:
```bash
cd tests
python test_db.py
```

**Test Coverage**:
- ✅ Database connection verification
- ✅ Table access and data retrieval
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Metadata operations (levels, types, series)
- ✅ Service layer functionality
- ✅ Response validation

## Running Tests

### Prerequisites
1. **Environment Setup**: Ensure virtual environment is activated
   ```bash
   .venv\Scripts\Activate.ps1
   ```

2. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration**: Verify `.env` file is properly configured
   ```env
   DATABASE_URL=your_connection_string
   # Database connection details
   ```

4. **Database Access**: Ensure database is accessible and has sample data

### Running Database Tests
```bash
# From project root
cd tests
python test_db.py
```

### Expected Output
```
🚀 PDC Classification Database Test
==================================================
🔗 Testing database connection...
✅ Database connection successful!
📋 Testing table access...
📊 Total classifications in table: 3
📄 Sample records:
  ID: 1 | Name: Employee Termination File | Code: HR_TERM_001 | Level: Confidential | Active: True
  ID: 2 | Name: Executed Contracts | Code: LEGAL_CONTRACT_002 | Level: Restricted | Active: True
  ID: 3 | Name: Annual Financial Statement | Code: FIN_STAT_003 | Level: Confidential | Active: True
🔧 Testing CRUD operations...
✅ get_all(): Found 3 total records, retrieved 3
✅ get_by_id(): Retrieved 'Annual Financial Statement' (ID: 3)
✅ get_by_code(): Retrieved 'Annual Financial Statement' (Code: FIN_STAT_003)
📊 Testing metadata operations...
✅ Classification levels: ['Confidential', 'Restricted']
✅ Media types: ['sample_doc', 'thumbnail']
✅ File types: ['DOCX', 'PDF']
✅ Series: ['Financial Reports', 'HR Records', 'Legal Contracts']
==================================================
🎉 All tests passed successfully!

🔗 Your API endpoints are ready:
  GET  /api/classifications
  GET  /api/classifications/{id}
  POST /api/classifications
  PUT  /api/classifications/{id}
  DELETE /api/classifications/{id}
  GET  /api/classifications/metadata
  GET  /api/health
```

## Postman Tests

For API endpoint testing, see the `/postman` directory which contains:
- Complete Postman collection with 12 comprehensive tests
- Environment configuration
- Detailed API testing documentation

## Test Categories

### 1. **Database Tests** (`test_db.py`)
- **Connection Tests**: Verify database connectivity
- **Table Access**: Test raw table access and data retrieval
- **Service Layer**: Test business logic and data operations
- **Metadata**: Test metadata aggregation functions

### 2. **API Tests** (Postman Collection)
- **HTTP Endpoints**: Test all REST API endpoints
- **CRUD Operations**: Full Create, Read, Update, Delete testing
- **Error Handling**: Test error responses and validation
- **Performance**: Response time and load testing

## Adding New Tests

### For Python Tests
1. Create test files in the `/tests` directory
2. Follow naming convention: `test_*.py`
3. Add proper import path handling:
   ```python
   # Add the project root to Python path (go up one level from tests/)
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

### Test Structure Template
```python
"""
Test description and purpose.
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.config import get_db
from services.pdc_service import PDCClassificationCRUD

def test_function_name():
    """Test specific functionality."""
    try:
        # Test implementation
        print("✅ Test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 Test Suite Name")
    print("=" * 50)
    
    success = True
    
    if not test_function_name():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()
```

## Test Data

### Sample Data Used
The tests work with existing sample data in the database:
- Employee Termination File (HR_TERM_001)
- Executed Contracts (LEGAL_CONTRACT_002) 
- Annual Financial Statement (FIN_STAT_003)

### Test Data Safety
- Tests are **read-only** by default
- No test data is modified or deleted
- Safe to run against production-like data
- Creates minimal temporary data for create/update tests

## Troubleshooting

### Common Test Failures

**1. Database Connection Issues**
```
❌ Database connection error: (pyodbc.Error)
```
- Check `.env` file configuration
- Verify database server accessibility
- Ensure proper authentication

**2. Import Errors**
```
ModuleNotFoundError: No module named 'database'
```
- Run tests from correct directory (`tests/`)
- Verify virtual environment is activated
- Check project structure is intact

**3. Data Validation Errors**
```
❌ Error testing CRUD operations
```
- Verify database has sample data
- Check table structure matches models
- Ensure required fields are populated

**4. Service Layer Errors**
```
❌ Error testing metadata operations
```
- Check service layer implementations
- Verify database permissions
- Test individual service methods

### Debugging Tests

1. **Enable Detailed Logging**: Add debug prints to test functions
2. **Run Individual Tests**: Comment out other tests to isolate issues
3. **Check Database State**: Verify sample data exists and is accessible
4. **Validate Models**: Ensure model definitions match database schema

### Getting Help

When tests fail:
1. Read the error message carefully
2. Check database connectivity first
3. Verify environment configuration
4. Review test output for specific failure points
5. Check related API functionality manually