# PDC Classifications & Lookup API - Postman Collections v4.0.0

This directory contains Postman collection and environment files for testing the complete PDC Classifications and Lookup API, including **unified service architecture** with advanced pagination features (offset & cursor-based), blueprint organization, and batch endpoints.

## Files

- `PDC_Classifications_API.postman_collection.json` - Complete API test collection with unified service architecture (v4.0.0)
- `PDC_Classifications.postman_environment.json` - Environment variables for the collection
- `README.md` - This documentation

## 🆕 What's New in v4.0.0

### **🏗️ Unified Service Architecture**
- **Single Service Interface**: Both Classifications and Lookups now use unified services
- **Eliminated Duplication**: No more separate basic and enhanced services
- **Consistent Architecture**: Classification and Lookup services follow the same pattern
- **Template Name Support**: Classifications now include template names in responses
- **Consolidated Methods**: All CRUD, pagination, and utility methods in one service

### **🔧 Service Architecture Updates**
- **PDCClassificationService**: Unified service with all classification functionality
- **PDCLookupService**: Unified service with all lookup functionality  
- **Preserved Functionality**: All advanced pagination and filtering capabilities maintained
- **Cleaner Imports**: Simplified service imports across all endpoints
- **Better Testing**: Single services easier to test and maintain

## 🎯 Previous Features (v3.0.0)

### **Advanced Pagination Support**
- **Offset Pagination**: Traditional page-based navigation with page numbers
- **Cursor Pagination**: High-performance pagination using cursor tokens
- **Enhanced Response Format**: Structured responses with `items`, `pagination`, and `metadata`
- **Advanced Filtering**: Multiple filter combinations with ranges, arrays, and search
- **Performance Tracking**: Execution time monitoring and optimization metrics

### **Test Categories**
- **Pagination - Offset Advanced**: Tests complex filtering with offset pagination
- **Pagination - Cursor Based**: Tests high-performance cursor pagination
- **Pagination - With Search**: Tests full-text search combined with pagination
- **Pagination - Multiple Filters**: Tests complex multi-filter scenarios
- **Enhanced Summary Endpoints**: Tests new summary statistics endpoints

## 🏗️ **Unified Service Architecture**

### **Before (v3.0.0) - Dual Services**
```
services/
├── pdc_service.py               # Basic classification CRUD
├── enhanced_pdc_service.py      # Advanced classification features
├── lookup_service.py            # Basic lookup CRUD  
└── enhanced_lookup_service.py   # Advanced lookup features
```

### **After (v4.0.0) - Unified Services**
```
services/
├── classification_service.py    # ALL classification functionality
└── lookup_service.py           # ALL lookup functionality
```

### **Benefits of Unified Architecture**
- ✅ **Single Service Interface**: One service handles all operations
- ✅ **Eliminated Duplication**: No more duplicate methods between services
- ✅ **Consistent Pattern**: Both services follow the same architecture
- ✅ **Template Name Support**: Classifications include template names
- ✅ **Easier Maintenance**: Single service to update and test
- ✅ **Cleaner Code**: Simplified imports and reduced complexity

## Collection Structure

The collection reflects the blueprint architecture and includes comprehensive tests for all API domains:

### 🏥 Health & Diagnostics
- **Basic Health Check** - Simple connectivity and status check
- **Detailed Health Check** - Component-level health monitoring
- **Diagnostic Information** - System configuration and troubleshooting

### 📋 Classifications
- **Get All Classifications** - Enhanced pagination with new response structure
- **Get Classification by ID** - Single resource retrieval
- **Create New Classification** - Full CRUD with validation
- **Update Classification** - Partial updates with validation
- **Delete Classification (Soft)** - Soft delete with tracking
- **Restore Classification** - Restore soft-deleted records
- **Track Access** - Access logging and tracking
- **Get Metadata** - System metadata and configuration
- **Get by Organization** - Organization-specific filtering
- **Get by Sensitivity** - Sensitivity-based filtering

#### 🆕 Advanced Features Tests (v4.0.0)
- **Template Name Integration** - All classification responses now include template names
- **Pagination - Offset Advanced** - Complex filtering with offset pagination
- **Pagination - Cursor Based** - High-performance cursor pagination with tokens
- **Pagination - With Search** - Full-text search across multiple fields
- **Pagination - Multiple Filters** - Complex multi-filter combinations
- **Get Classifications Summary** - Enhanced statistics and aggregation data
- **Unified Service Testing** - All tests now use the unified service architecture

### 🔍 Lookups
- **Get All Lookup Types** - Paginated lookup type listing
- **Get Specific Lookup Type** - Single lookup type details
- **Get Lookup Type with Codes** - Type with associated codes
- **Get Lookup Codes by Type** - Enhanced pagination for codes by type
- **Get Specific Lookup Code** - Single code details
- **Get Summary Statistics** - System-wide lookup statistics

#### 🆕 Enhanced Lookup Pagination Tests
- **Lookup Codes - All with Pagination** - Get all codes with advanced pagination
- **Lookup Codes - By Type Enhanced** - Type-specific enhanced pagination
- **Lookup Codes - Cursor Pagination** - High-performance cursor-based navigation
- **Lookup Codes - Advanced Filtering** - Parent/child filters with search
- **Lookup Types Summary Enhanced** - Detailed statistics with counts by type

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

### 🚀 **NEW: Advanced Pagination Testing**
- **Offset vs Cursor Performance** - Comparative performance testing between pagination strategies
- **Pagination Math Validation** - Automatic validation of page counts, totals, and navigation
- **Filter Application Testing** - Verification that filters are properly applied and reflected in metadata
- **Search Result Validation** - Ensures search terms properly filter results across multiple fields
- **Sort Order Verification** - Validates that results are sorted correctly by specified criteria
- **Cursor Token Management** - Tests cursor token generation and usage for seamless navigation
- **Metadata Structure Testing** - Validates new response structure with pagination and metadata objects

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

### 🆕 Pagination Configuration
- `next_cursor` - Stores cursor tokens for cursor pagination tests
- `lookup_next_cursor` - Stores lookup-specific cursor tokens
- `test_page_size` - Configurable page size for testing (default: 10)

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
📋 Classifications → Test core CRUD + enhanced pagination
🔍 Lookups → Test lookup retrieval + advanced filtering
🔄 Batch Lookups → Test batch operations
❌ Error Handling → Validate error scenarios
```

## 📖 **Advanced Pagination Usage Guide**

### **Offset Pagination (Traditional)**
Perfect for user interfaces with page numbers and when you need total counts.

#### **Basic Offset Pagination:**
```
GET /api/classifications?page=1&size=20
GET /api/lookups/codes?page=2&size=50
```

#### **Offset with Sorting:**
```
GET /api/classifications?page=1&size=10&sort_by=name&sort_order=asc
GET /api/lookups/codes?page=1&size=25&sort_by=sort_order&sort_order=asc
```

#### **Offset with Filtering:**
```
GET /api/classifications?page=1&size=15&is_active=true&sensitivity_min=3
GET /api/lookups/codes?page=1&size=20&lookup_type=STATUS&is_active=true
```

### **Cursor Pagination (High Performance)**
Perfect for large datasets, real-time feeds, and mobile applications.

#### **Initial Cursor Request:**
```
GET /api/classifications?pagination_type=cursor&size=20
```

#### **Subsequent Cursor Requests:**
```
GET /api/classifications?pagination_type=cursor&size=20&cursor=eyJpZCI6MTIzNH0=
```

#### **Cursor with Filtering:**
```
GET /api/lookups/codes?pagination_type=cursor&size=30&is_active=true
```

### **Advanced Filtering Examples**

#### **Classifications - Complex Filters:**
```
# Multiple organization filter
GET /api/classifications?organization_ids=1,2,3&is_active=true&size=50

# Sensitivity range filter
GET /api/classifications?sensitivity_min=2&sensitivity_max=7&page=1&size=25

# Classification level filter
GET /api/classifications?classification_levels=SECRET,TOP_SECRET&page=1&size=20

# Date range filter  
GET /api/classifications?created_after=2023-01-01T00:00:00Z&created_before=2023-12-31T23:59:59Z
```

#### **Lookups - Advanced Filters:**
```
# Parent codes only
GET /api/lookups/codes?parent_codes_only=true&is_active=true&page=1&size=30

# Child codes only
GET /api/lookups/codes?child_codes_only=true&sort_by=name&sort_order=asc

# Multiple lookup types
GET /api/lookups/codes?lookup_types=STATUS,PRIORITY,CATEGORY&page=1&size=100

# Sort order range
GET /api/lookups/codes?sort_order_min=10&sort_order_max=50&page=1&size=25
```

### **Search with Pagination**

#### **Full-Text Search:**
```
# Search classifications
GET /api/classifications?search=secret&page=1&size=20&sort_by=name

# Search lookups
GET /api/lookups/codes?search=active&lookup_type=STATUS&page=1&size=15
```

#### **Search Fields Covered:**
- **Classifications**: `name`, `description`, `code`, `series`, `classification_purpose`, `classification_level`, `media_type`, `file_type`
- **Lookups**: `code`, `name`, `description`, `lookup_type`, `additional_info`

### **New Response Structure**

#### **Enhanced Response Format:**
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_previous": false,
    "next_cursor": "eyJpZCI6MTIzNH0=",
    "previous_cursor": null
  },
  "metadata": {
    "filters_applied": {
      "is_active": true,
      "sensitivity_min": 3
    },
    "sort_info": {
      "sort_by": "name",
      "sort_order": "asc"
    },
    "search_term": "secret",
    "total_filtered": 150,
    "execution_time_ms": 45.2
  }
}
```

### **Performance Guidelines**

#### **When to Use Offset Pagination:**
- Small to medium datasets (< 10,000 records)
- User interfaces requiring page numbers
- When total count is needed
- Simple sorting and filtering scenarios

#### **When to Use Cursor Pagination:**
- Large datasets (> 10,000 records)  
- Real-time data feeds
- Mobile applications
- High-frequency API calls
- When consistent performance is critical

#### **Performance Tips:**
- Use specific filters to reduce dataset size
- Keep page sizes under 100 items
- Use cursor pagination for large datasets
- Limit sorting to indexed fields
- Cache frequently accessed data

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
✅ Get All Classifications: 6/6 tests passed (enhanced pagination structure)
✅ Get Classification by ID: 3/3 tests passed
✅ Create New Classification: 4/4 tests passed
✅ Update Classification: 4/4 tests passed
✅ Delete Classification (Soft): 3/3 tests passed
✅ Restore Classification: 3/3 tests passed
✅ Track Access: 3/3 tests passed
✅ Get Metadata: 3/3 tests passed
✅ Get by Organization: 3/3 tests passed
✅ Get by Sensitivity: 3/3 tests passed

🆕 Advanced Pagination Tests
✅ Pagination - Offset Advanced: 5/5 tests passed
✅ Pagination - Cursor Based: 3/3 tests passed  
✅ Pagination - With Search: 2/2 tests passed
✅ Pagination - Multiple Filters: 2/2 tests passed
✅ Get Classifications Summary: 3/3 tests passed

🔍 Lookups  
✅ Get All Lookup Types: 4/4 tests passed
✅ Get Specific Lookup Type: 3/3 tests passed
✅ Get Lookup Type with Codes: 4/4 tests passed
✅ Get Lookup Codes by Type: 4/4 tests passed (enhanced pagination)
✅ Get Specific Lookup Code: 3/3 tests passed
✅ Get Summary Statistics: 3/3 tests passed

🆕 Enhanced Lookup Pagination Tests
✅ Lookup Codes - All with Pagination: 3/3 tests passed
✅ Lookup Codes - By Type Enhanced: 3/3 tests passed
✅ Lookup Codes - Cursor Pagination: 3/3 tests passed
✅ Lookup Codes - Advanced Filtering: 3/3 tests passed
✅ Lookup Types Summary Enhanced: 3/3 tests passed

🔄 Batch Lookups
✅ Batch Lookup (POST): 4/4 tests passed
✅ Batch Lookup (GET): 3/3 tests passed
✅ Large Batch Lookup Test: 4/4 tests passed

❌ Error Handling
✅ 404 - Non-existent Classification: 3/3 tests passed
✅ 404 - Non-existent Lookup Type: 3/3 tests passed
✅ 400 - Invalid Classification Data: 3/3 tests passed
✅ 400 - Invalid Batch Request: 3/3 tests passed

Total: 97+/97+ tests passed ✅ (Enhanced with Unified Architecture + Template Names)
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

**4. 🆕 Unified Architecture Issues (v4.0.0)**
- **Missing Template Names**: Verify template_name field exists in all classification responses
- **Service Import Errors**: Ensure unified services are properly deployed
- **Method Not Found**: Check that all CRUD operations use the unified service methods
- **Response Structure Changes**: Verify no breaking changes in API responses

**5. 🆕 Pagination Issues**
- **Cursor Errors**: Ensure cursor tokens are properly encoded and not expired
- **Filter Failures**: Check filter parameter syntax and data types
- **Performance Issues**: Use cursor pagination for datasets > 10,000 records
- **Sort Field Errors**: Verify sort fields exist and are properly indexed

**6. Database Connection Issues**
- Check environment variables in diagnostic endpoint
- Verify Azure SQL authentication method
- Test individual endpoints before running full collection

### Performance Benchmarks

Expected response times for different operations:
- Health checks: < 2 seconds
- Single record retrieval: < 2 seconds  
- **Offset pagination**: < 3 seconds (small-medium datasets)
- **Cursor pagination**: < 1 second (consistent performance)
- Batch operations: < 5 seconds
- Large batch operations: < 10 seconds
- **Advanced filtering**: < 2 seconds (with proper indexing)
- **Full-text search**: < 3 seconds (depends on dataset size)

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

# Test pagination performance specifically
newman run PDC_Classifications_API.postman_collection.json \
  -e PDC_Classifications.postman_environment.json \
  --folder "Classifications" \
  --grep "Pagination" \
  --reporters cli,json \
  --reporter-json-export pagination-results.json
```

## 🆕 **Quick Unified Architecture Test Guide**

### **Step 1: Template Name Feature Test**
1. Run "Get All Classifications" - Check for template_name field in response items
2. Run "Get Classification by ID" - Verify template_name is included in single responses
3. Look for console logs showing template names: `✅ Template name field found:`

### **Step 2: Unified Service Validation**
1. All endpoints should work seamlessly (no service-related errors)
2. Response formats remain consistent with v3.0.0
3. All CRUD operations continue to function normally
4. Advanced pagination still works with unified services

### **Step 3: Architecture Benefits Verification**  
- No duplicate method calls or conflicting services
- Consistent response times across similar operations  
- Cleaner error messages (no service confusion)
- All functionality preserved from separate services

## 🆕 **Quick Pagination Test Guide**

### **Step 1: Basic Pagination Test**
1. Run "Get All Classifications" - Should show new response structure
2. Check `pagination` object has all required fields
3. Verify `metadata` contains filter and sort information

### **Step 2: Advanced Offset Pagination**
1. Run "Pagination - Offset Advanced" 
2. Verify filters are applied correctly
3. Check pagination math (pages = ceil(total/size))
4. Ensure sorting works as specified

### **Step 3: Cursor Pagination Test**
1. Run "Pagination - Cursor Based"
2. Verify `next_cursor` is returned when there are more results
3. Check that `total` is -1 (not calculated for performance)
4. Test cursor token storage in collection variables

### **Step 4: Search and Filtering**
1. Run "Pagination - With Search"
2. Verify search results contain search terms
3. Run "Pagination - Multiple Filters" 
4. Check that all filters are reflected in metadata

### **Step 5: Lookup Pagination**
1. Run all "Lookup Codes" pagination tests
2. Test type-specific pagination
3. Verify parent/child filtering works
4. Check enhanced summary endpoints

### **Expected New Response Format:**
All paginated endpoints now return:
```json
{
  "items": [...],           // The actual data
  "pagination": {...},      // Page info, cursors, totals
  "metadata": {...}         // Filters applied, sort info, performance
}
```

### **Testing Checklist:**
- [ ] Basic offset pagination works
- [ ] Cursor pagination generates tokens
- [ ] Filters are applied and reflected in metadata
- [ ] Search works across multiple fields
- [ ] Sort order is correctly applied
- [ ] Performance times are within acceptable ranges
- [ ] Summary endpoints return aggregate data
- [ ] Error handling works for invalid parameters