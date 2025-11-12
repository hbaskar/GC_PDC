# PDC Classifications & Lookup API - Postman Collections

This directory contains Postman collection and environment files for testing the complete PDC Classifications and Lookup API, including the new blueprint organization and batch endpoints.

## Files

- `PDC_Classifications_API.postman_collection.json` - Complete API test collection with blueprint organization
- `PDC_Classifications.postman_environment.json` - Environment variables for the collection
- `README.md` - This documentation

## Collection Structure

The collection reflects the blueprint architecture and includes comprehensive tests for all API domains:

### 🏥 Health & Diagnostics
- **Basic Health Check** - Simple connectivity and status check
- **Detailed Health Check** - Component-level health monitoring
- **Diagnostic Information** - System configuration and troubleshooting

### 📋 Classifications
- **Get All Classifications** - Pagination, filtering, and search
- **Get Classification by ID** - Single resource retrieval
- **Create New Classification** - Full CRUD with validation
- **Update Classification** - Partial updates with validation
- **Delete Classification (Soft)** - Soft delete with tracking
- **Restore Classification** - Restore soft-deleted records
- **Track Access** - Access logging and tracking
- **Get Metadata** - System metadata and configuration
- **Get by Organization** - Organization-specific filtering
- **Get by Sensitivity** - Sensitivity-based filtering

### 🔍 Lookups
- **Get All Lookup Types** - Paginated lookup type listing
- **Get Specific Lookup Type** - Single lookup type details
- **Get Lookup Type with Codes** - Type with associated codes
- **Get Lookup Codes by Type** - Paginated code listing
- **Get Specific Lookup Code** - Single code details
- **Get Summary Statistics** - System-wide lookup statistics

### 🔄 Batch Lookups (New!)
- **Batch Lookup (POST)** - JSON-based batch retrieval
- **Batch Lookup (GET)** - Query parameter-based batch retrieval
- **Large Batch Lookup Test** - Performance testing for multiple types

### ❌ Error Handling
- **404 - Non-existent Classification** - Resource not found testing
- **404 - Non-existent Lookup Type** - Lookup-specific 404 testing  
- **400 - Invalid Classification Data** - Validation error testing
- **400 - Invalid Batch Request** - Batch validation error testing

## Key Features

### 🚀 Key Features
- **Blueprint Architecture Testing** - Tests organized by blueprint modules
- **Batch Lookup Operations** - Efficient multi-type lookup retrieval
- **Enhanced Health Monitoring** - Detailed component health checks
- **Comprehensive Error Testing** - Domain-specific error scenarios
- **Performance Benchmarking** - Response time and payload size validation

### 🧪 Advanced Testing Features
- **Automated Variable Management** - Dynamic ID capture and reuse
- **Response Structure Validation** - Schema compliance checking
- **Performance Assertions** - Response time limits and payload size checks
- **Cross-Domain Workflow Testing** - Multi-endpoint test scenarios
- **Error Recovery Testing** - Soft delete and restore workflows

## Environment Variables

### Base Configuration
- `base_url` - API base URL (default: http://localhost:7071)
- `classification_id` - Used for classification operations
- `created_classification_id` - Auto-populated after CREATE operations
- `test_code` - Auto-generated unique code for testing

### Lookup Configuration  
- `lookup_type` - Default lookup type for testing (STATUS)
- `lookup_code` - Default lookup code for testing (ACTIVE)
- `batch_lookup_types` - Comma-separated types for batch testing

### Dynamic Variables
- `access_classification_id` - Used for access tracking tests
- Variables are automatically populated during test execution

## Usage

### Quick Start
1. Import `PDC_Classifications_API.postman_collection.json` into Postman
2. Import `PDC_Classifications.postman_environment.json` as environment
3. Select the "PDC Classifications & Lookup Environment"
4. Run individual requests or entire folders

### Organized Testing
```
🏥 Health & Diagnostics → Test system health first
📋 Classifications → Test core CRUD operations  
🔍 Lookups → Test lookup retrieval
🔄 Batch Lookups → Test batch operations
❌ Error Handling → Validate error scenarios
```

### Newman CLI Usage
```bash
# Run complete collection
newman run PDC_Classifications_API.postman_collection.json \
  -e PDC_Classifications.postman_environment.json

# Run specific folder
newman run PDC_Classifications_API.postman_collection.json \
  -e PDC_Classifications.postman_environment.json \
  --folder "Batch Lookups"

# Generate detailed report
newman run PDC_Classifications_API.postman_collection.json \
  -e PDC_Classifications.postman_environment.json \
  --reporters html,cli \
  --reporter-html-export report.html
```

## Test Coverage

### 📊 Comprehensive Coverage
- **Response Validation** - Status codes, headers, structure
- **Data Integrity** - Field validation, type checking, business rules
- **Performance Monitoring** - Response times, payload sizes
- **Error Handling** - All error scenarios and edge cases
- **Workflow Testing** - Multi-step operations and state management

### 🎯 Blueprint-Specific Testing
- **Classifications Blueprint** - Complete CRUD + advanced features
- **Lookups Blueprint** - Type/code management + batch operations  
- **Health Blueprint** - System monitoring + diagnostics

### 🔍 Batch Operation Testing
- **Single Type Batch** - Simple batch retrieval validation
- **Multi-Type Batch** - Complex batch operation testing
- **Large Batch Performance** - Scalability and performance testing
- **Error Scenarios** - Invalid requests, missing types, limits

## Expected Test Results

When all tests pass, you should see:

```
🏥 Health & Diagnostics
✅ Basic Health Check: 3/3 tests passed
✅ Detailed Health Check: 3/3 tests passed  
✅ Diagnostic Information: 3/3 tests passed

📋 Classifications
✅ Get All Classifications: 4/4 tests passed
✅ Get Classification by ID: 3/3 tests passed
✅ Create New Classification: 4/4 tests passed
✅ Update Classification: 4/4 tests passed
✅ Delete Classification (Soft): 3/3 tests passed
✅ Restore Classification: 3/3 tests passed
✅ Track Access: 3/3 tests passed
✅ Get Metadata: 3/3 tests passed
✅ Get by Organization: 3/3 tests passed
✅ Get by Sensitivity: 3/3 tests passed

🔍 Lookups  
✅ Get All Lookup Types: 4/4 tests passed
✅ Get Specific Lookup Type: 3/3 tests passed
✅ Get Lookup Type with Codes: 4/4 tests passed
✅ Get Lookup Codes by Type: 4/4 tests passed
✅ Get Specific Lookup Code: 3/3 tests passed
✅ Get Summary Statistics: 3/3 tests passed

🔄 Batch Lookups
✅ Batch Lookup (POST): 4/4 tests passed
✅ Batch Lookup (GET): 3/3 tests passed
✅ Large Batch Lookup Test: 4/4 tests passed

❌ Error Handling
✅ 404 - Non-existent Classification: 3/3 tests passed
✅ 404 - Non-existent Lookup Type: 3/3 tests passed
✅ 400 - Invalid Classification Data: 3/3 tests passed
✅ 400 - Invalid Batch Request: 3/3 tests passed

Total: 73/73 tests passed ✅
```

## Troubleshooting

### Common Issues

**1. Health Check Failures**
- Ensure Azure Functions is running: `func start`
- Check database connectivity in diagnostic endpoint
- Verify SQLAlchemy text() wrapping is working

**2. Blueprint Organization Issues**
- Verify all blueprints are registered in `function_app.py`
- Check import statements in blueprint files
- Ensure no circular import dependencies

**3. Batch Lookup Failures**
- Verify lookup types exist in your database
- Check payload size limits (default: 50KB)
- Ensure proper case sensitivity for lookup types

**4. Database Connection Issues**
- Check environment variables in diagnostic endpoint
- Verify Azure SQL authentication method
- Test individual endpoints before running full collection

### Performance Benchmarks

Expected response times for different operations:
- Health checks: < 2 seconds
- Single record retrieval: < 2 seconds  
- Paginated lists: < 3 seconds
- Batch operations: < 5 seconds
- Large batch operations: < 10 seconds

### Debug Mode

To enable detailed debugging:
1. Open Postman Console (View → Show Postman Console)
2. Run tests with console open to see detailed logs
3. Check `console.log()` statements in test scripts
4. Review request/response details for failed tests

## Integration Examples

### CI/CD Pipeline Integration
```yaml
# GitHub Actions example
- name: Test PDC API
  run: |
    npm install -g newman
    newman run postman/PDC_Classifications_API_v2.postman_collection.json \
      -e postman/PDC_API_v2.postman_environment.json \
      --reporters junit,cli \
      --reporter-junit-export results.xml
      
- name: Publish Test Results
  uses: dorny/test-reporter@v1
  if: always()
  with:
    name: API Tests
    path: results.xml
    reporter: java-junit
```

### Load Testing with Newman
```bash
# Run collection multiple times for load testing
for i in {1..10}; do
  echo "Run $i"
  newman run PDC_Classifications_API.postman_collection.json \
    -e PDC_Classifications.postman_environment.json \
    --folder "Batch Lookups" \
    --delay-request 100
done
```