# PDC Classification API

A comprehensive Azure Functions-based API for managing Product Data Classification (PDC) records using SQLAlchemy ORM with Azure SQL Database.

## Features

- **Full CRUD Operations**: Create, Read, Update, Delete PDC classifications
- **Advanced Filtering**: Filter by active status, category, and search across multiple fields
- **Pagination**: Built-in pagination support for large datasets
- **Soft Delete**: Optional soft delete functionality
- **Data Validation**: Comprehensive input validation using Pydantic schemas
- **Error Handling**: Standardized error responses with proper HTTP status codes
- **Health Check**: Database connection health monitoring

## Project Structure

```
gc_pdc/
├── database/
│   ├── __init__.py
│   ├── config.py          # Database configuration and connection
│   └── models.py          # SQLAlchemy models
├── schemas/
│   ├── __init__.py
│   └── classification_schemas.py     # Pydantic schemas for validation
├── services/
│   ├── __init__.py
│   └── classification_service.py     # CRUD operations service
├── scripts/               # Database utilities and maintenance scripts
│   ├── __init__.py
│   ├── README.md          # Scripts documentation
│   ├── find_classification_tables.py   # Discover classification tables
│   ├── inspect_tables.py              # Comprehensive table inspection
│   └── inspect_pdc_classifications.py # Focused pdc_classifications analysis
├── tests/                 # Test scripts and utilities
│   ├── __init__.py
│   ├── README.md          # Testing documentation
│   └── test_db.py         # Database and service layer tests
├── postman/               # API testing collection
│   ├── PDC_Classifications_API.postman_collection.json
│   ├── PDC_Classifications.postman_environment.json
│   └── README.md          # Postman testing guide
├── function_app.py        # Azure Functions endpoints
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── host.json             # Azure Functions host configuration
└── local.settings.json   # Local development settings
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file (or copy from `.env.example`) with your database connection details.

#### Option A: SQL Authentication
```env
# Choose authentication method
AZURE_SQL_AUTH_METHOD=sql

# Database connection details
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=CMSDEVB
AZURE_SQL_USERNAME=your-username
AZURE_SQL_PASSWORD=your-password
AZURE_SQL_AUTHENTICATION=ActiveDirectoryPassword
```

#### Option B: Managed Identity (Azure environments)
```env
# Choose authentication method
AZURE_SQL_AUTH_METHOD=managed_identity

# Database connection details (no credentials needed)
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=CMSDEVB

# Optional: For User-Assigned Managed Identity
# AZURE_CLIENT_ID=your-managed-identity-client-id
```

#### Common Settings
```env
# Optional database settings
AZURE_SQL_PORT=1433
AZURE_SQL_DRIVER=ODBC Driver 18 for SQL Server
```

### 3. Initialize Database

Run the database initialization script:

```bash
python test_db.py
```

This will:
- Test the database connection
- Create the required tables
- Insert sample data
- Verify CRUD operations

### 4. Start the Azure Functions Host

```bash
func host start
```

The API will be available at `http://localhost:7071`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check API and database health

### Classifications Management

#### Get All Classifications
- **GET** `/api/classifications`
- **Query Parameters:**
  - `page` (int): Page number (default: 1)
  - `size` (int): Page size (default: 20)
  - `is_active` (bool): Filter by active status
  - `category` (string): Filter by category
  - `search` (string): Search across name, description, and code

**Example:**
```bash
curl "http://localhost:7071/api/classifications?page=1&size=10&is_active=true&search=confidential"
```

#### Get Classification by ID
- **GET** `/api/classifications/{id}`

**Example:**
```bash
curl "http://localhost:7071/api/classifications/1"
```

#### Create New Classification
- **POST** `/api/classifications`
- **Content-Type:** `application/json`

**Request Body:**
```json
{
  "name": "Top Secret",
  "description": "Highest level of classification",
  "code": "TS",
  "category": "Security",
  "is_active": true,
  "created_by": "admin"
}
```

**Example:**
```bash
curl -X POST "http://localhost:7071/api/classifications" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Top Secret",
    "description": "Highest level of classification",
    "code": "TS",
    "category": "Security",
    "created_by": "admin"
  }'
```

#### Update Classification
- **PUT** `/api/classifications/{id}`
- **Content-Type:** `application/json`

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "is_active": false,
  "updated_by": "admin"
}
```

**Example:**
```bash
curl -X PUT "http://localhost:7071/api/classifications/1" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated classification description",
    "updated_by": "admin"
  }'
```

#### Delete Classification
- **DELETE** `/api/classifications/{id}`
- **Query Parameters:**
  - `soft` (bool): Use soft delete (default: true)
  - `deleted_by` (string): User performing the deletion (for soft delete)

**Examples:**
```bash
# Soft delete (sets is_active = false)
curl -X DELETE "http://localhost:7071/api/classifications/1?soft=true&deleted_by=admin"

# Hard delete (removes from database)
curl -X DELETE "http://localhost:7071/api/classifications/1?soft=false"
```

#### Get Categories
- **GET** `/api/classifications/categories` - Get all unique categories

**Example:**
```bash
curl "http://localhost:7071/api/classifications/categories"
```

## Data Models

### PDC Classification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | int | Auto | Primary key |
| name | string(255) | Yes | Classification name |
| description | text | No | Detailed description |
| code | string(50) | Yes | Unique classification code |
| category | string(100) | No | Classification category |
| is_active | boolean | No | Active status (default: true) |
| created_at | datetime | Auto | Creation timestamp |
| updated_at | datetime | Auto | Last update timestamp |
| created_by | string(255) | No | User who created the record |
| updated_by | string(255) | No | User who last updated the record |

## Response Formats

### Success Response
```json
{
  "id": 1,
  "name": "Confidential",
  "description": "Information that could cause harm if disclosed",
  "code": "CONF",
  "category": "Security",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": null,
  "created_by": "system",
  "updated_by": null
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### Error Response
```json
{
  "error": "Classification not found",
  "detail": "No classification found with ID 999",
  "status_code": 404
}
```

## Database Schema

The API automatically creates the following table structure:

```sql
CREATE TABLE pdc_classifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    description NTEXT,
    code NVARCHAR(50) NOT NULL UNIQUE,
    category NVARCHAR(100),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2,
    created_by NVARCHAR(255),
    updated_by NVARCHAR(255)
);

CREATE INDEX IX_pdc_classifications_name ON pdc_classifications(name);
CREATE INDEX IX_pdc_classifications_code ON pdc_classifications(code);
CREATE INDEX IX_pdc_classifications_category ON pdc_classifications(category);
```

## Testing

### 🏗️ Architecture & Feature Tests
```bash
# Test unified service architecture
python test_lookup_unification.py
python test_template_name.py

# Test blueprint architecture
python test_blueprints.py

# Test Postman collection compatibility 
python test_postman_compatibility.py
```

### 🗄️ Database and Service Layer Tests
```bash
# Run formal database tests
python -m pytest tests/

# Run comprehensive database tests
python tests/test_db.py

# Test unified services
python scripts/test_lookup_service.py
python scripts/test_database_connection.py
```

### 🌐 API Endpoint Testing
Use the comprehensive Postman collection v4.0.0 provided in the `/postman` directory:

1. **Import Collection**: Import `PDC_Classifications_API.postman_collection.json` (v4.0.0)
2. **Import Environment**: Import `PDC_Classifications.postman_environment.json` 
3. **Run Tests**: Execute individual tests or run entire collection
4. **View Results**: See detailed test results with 97+ comprehensive validations including template name testing

**Key v4.0.0 Features:**
- ✅ Template name validation in classification responses
- ✅ Unified service architecture compatibility testing
- ✅ Advanced pagination with both offset and cursor support
- ✅ Batch lookup operations testing

**Alternative: Manual Testing**
```bash
# Health check
curl "http://localhost:7071/api/health"

# Get all classifications (with template names)
curl "http://localhost:7071/api/classifications"

# Get specific classification
curl "http://localhost:7071/api/classifications/1"

# Test advanced pagination
curl "http://localhost:7071/api/classifications?page=1&size=10&sort_by=name"
```

### 📊 Test Suite Organization

- **📋 **Root Directory**: Major feature and architecture tests**
  - `test_template_name.py` - Template name functionality 
  - `test_lookup_unification.py` - Unified service architecture
  - `test_postman_compatibility.py` - API compatibility testing
  - `test_blueprints.py` - Blueprint architecture validation

- **� `/tests`**: Formal test suite for CI/CD integration**
  - Database connectivity and service layer validation
  - Pytest-compatible test structure

- **📁 `/postman`**: Complete API endpoint testing (v4.0.0)**
  - 97+ test scenarios with unified architecture support
  - Template name feature validation
  - Advanced pagination testing

- **�️ `/scripts`**: Development and debugging tests**
  - Service operation testing
  - Database inspection utilities
  - Authentication method validation

### Authentication Testing
```bash
# Test authentication method configurations
python scripts/test_auth_methods.py
```

This script validates both SQL and Managed Identity authentication configurations without attempting actual connections.

## Authentication Methods

The application supports two authentication methods for connecting to Azure SQL Database:

### SQL Authentication (`AZURE_SQL_AUTH_METHOD=sql`)
Traditional username/password authentication with Azure Active Directory support.

**Use Cases:**
- Local development environments
- Non-Azure hosting environments  
- When explicit credentials are preferred
- Testing and development scenarios

**Required Environment Variables:**
```env
AZURE_SQL_AUTH_METHOD=sql
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=CMSDEVB
AZURE_SQL_USERNAME=your-username
AZURE_SQL_PASSWORD=your-password
AZURE_SQL_AUTHENTICATION=ActiveDirectoryPassword
```

### Managed Identity (`AZURE_SQL_AUTH_METHOD=managed_identity`)
Passwordless authentication using Azure Managed Identity for enhanced security.

**Use Cases:**
- Production Azure environments (Azure Functions, App Service, etc.)
- Enhanced security with no stored credentials
- Compliance requirements for passwordless authentication
- Simplified credential management

**Required Environment Variables:**
```env
AZURE_SQL_AUTH_METHOD=managed_identity
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=CMSDEVB
# Optional: AZURE_CLIENT_ID=client-id (for user-assigned identity)
```

**Prerequisites for Managed Identity:**
1. **System-Assigned Identity**: Enable system-assigned managed identity on your Azure resource
2. **User-Assigned Identity**: Create and assign a user-assigned managed identity
3. **Database Permissions**: Grant database access to the managed identity:
   ```sql
   CREATE USER [your-managed-identity-name] FROM EXTERNAL PROVIDER;
   ALTER ROLE db_datareader ADD MEMBER [your-managed-identity-name];
   ALTER ROLE db_datawriter ADD MEMBER [your-managed-identity-name];
   ```

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **404**: Not Found
- **409**: Conflict (duplicate code)
- **500**: Internal Server Error
- **503**: Service Unavailable (health check failure)

## Security Considerations

1. **Environment Variables**: Keep sensitive database credentials in environment variables
2. **Input Validation**: All inputs are validated using Pydantic schemas
3. **SQL Injection**: SQLAlchemy ORM provides protection against SQL injection
4. **Authentication**: Currently set to Anonymous for development; implement proper authentication for production

## Production Deployment

1. **Update host.json**: Configure extension bundles version
2. **Set Authentication**: Change `http_auth_level` from `ANONYMOUS` to `FUNCTION` or implement proper authentication
3. **Environment Variables**: Configure all required environment variables in Azure App Settings
4. **Connection Pooling**: The current configuration includes connection pooling settings
5. **Logging**: Configure Application Insights for production logging

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: 
   - Verify environment variables are set correctly
   - Check network connectivity to Azure SQL server
   - Run `python scripts/test_auth_methods.py` to validate configuration

2. **Authentication Issues**:
   - **SQL Auth**: Verify `AZURE_SQL_USERNAME` and `AZURE_SQL_PASSWORD` are correct
   - **Managed Identity**: Ensure identity is enabled and has database permissions
   - **Invalid Method**: Check `AZURE_SQL_AUTH_METHOD` is set to `sql` or `managed_identity`

3. **Managed Identity Setup**:
   - Enable system-assigned or create user-assigned managed identity
   - Grant database permissions to the managed identity
   - For user-assigned identity, set `AZURE_CLIENT_ID` environment variable

4. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`

5. **Table Access Issues**: Check database permissions and run `python tests/test_db.py`

### Authentication Troubleshooting

**Test Configuration**:
```bash
# Test your authentication setup
python scripts/test_auth_methods.py
```

**SQL Authentication Issues**:
- Verify credentials in `.env` file
- Check if Active Directory authentication is working
- Test with SQL Server Management Studio first

**Managed Identity Issues**:
- Verify managed identity is enabled on your Azure resource
- Check Azure SQL firewall allows Azure services
- Ensure managed identity has proper database roles:
  ```sql
  CREATE USER [your-managed-identity-name] FROM EXTERNAL PROVIDER;
  ALTER ROLE db_datareader ADD MEMBER [your-managed-identity-name];
  ALTER ROLE db_datawriter ADD MEMBER [your-managed-identity-name];
  ```

### Logging

Enable detailed logging by setting the log level in `host.json`:

```json
{
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true
      }
    },
    "logLevel": {
      "default": "Information"
    }
  }
}
```