# Scripts Directory

This directory contains utility scripts for database inspection, setup, and maintenance tasks.

## Scripts Overview

### Database Inspection Scripts

#### `find_classification_tables.py`
**Purpose**: Discover classification-related tables in the CMSDEVB database
- Searches for tables with names containing "classification", "pdc", "retention", etc.
- Provides table counts and basic structure information
- Useful for initial database exploration

**Usage**:
```bash
cd scripts
python find_classification_tables.py
```

#### `inspect_tables.py`
**Purpose**: Comprehensive table structure inspection and model generation
- Inspects multiple tables and their relationships
- Generates SQLAlchemy model code based on actual table structure
- Provides detailed column information including types, constraints, and indexes
- Can inspect specific tables or all tables in the database

**Usage**:
```bash
cd scripts
python inspect_tables.py
```

**Features**:
- Automatically detects foreign key relationships
- Generates proper SQLAlchemy column definitions
- Handles SQL Server specific data types
- Creates backup of generated models

#### `inspect_pdc_classifications.py`
**Purpose**: Focused inspection of the pdc_classifications table
- Detailed analysis of the main classifications table
- Sample data exploration
- Column-by-column analysis with data examples
- Generates optimized model specifically for pdc_classifications

**Usage**:
```bash
cd scripts
python inspect_pdc_classifications.py
```

**Output**:
- Table structure details
- Sample data from each column
- Suggested SQLAlchemy model code
- Data type recommendations

### Authentication Testing Scripts

#### `test_auth_methods.py`
**Purpose**: Test and validate authentication method configurations
- Tests SQL authentication configuration
- Tests System-Assigned Managed Identity setup
- Tests User-Assigned Managed Identity setup
- Validates error handling for invalid configurations
- Shows current environment configuration

**Usage**:
```bash
cd scripts
python test_auth_methods.py
```

**Features**:
- Validates connection string generation for both auth methods
- Tests environment variable handling
- Provides detailed configuration summary
- Safe testing (doesn't attempt actual database connections)
- Helps troubleshoot authentication setup issues

#### `test_database_connection.py`
**Purpose**: Test actual database connectivity with SQLAlchemy
- Tests engine creation and connection establishment
- Validates session management
- Provides real-world connection testing with actual queries

**Usage**:
```bash
cd scripts
python test_database_connection.py
```

#### `test_pyodbc_direct.py`
**Purpose**: Test direct pyodbc connections to isolate authentication issues
- Tests multiple authentication methods at the ODBC level
- Bypasses SQLAlchemy to isolate connection problems
- Useful for debugging authentication configuration

**Usage**:
```bash
cd scripts
python test_pyodbc_direct.py
```

#### `test_api_endpoints.py`
**Purpose**: Test Azure Functions app configuration
- Validates function app import and setup
- Tests function registration
- Ensures API endpoints are properly configured

**Usage**:
```bash
cd scripts
python test_api_endpoints.py
```

#### `debug_connection_string.py`
**Purpose**: Debug connection string generation and parameter conflicts
- Analyzes generated connection strings
- Identifies parameter conflicts
- Helps troubleshoot ODBC authentication issues

### Authentication Methods Supported

1. **SQL Authentication** (`AZURE_SQL_AUTH_METHOD=sql`)
   - Uses Azure Active Directory Password authentication (`ActiveDirectoryPassword`)
   - Configured via environment variables with full email format username
   - Uses custom SQLAlchemy connection creator to handle ODBC parameters correctly
   - Suitable for local development with Azure AD accounts

2. **Managed Identity** (`AZURE_SQL_AUTH_METHOD=managed_identity`)
   - Uses Azure Managed Identity for authentication
   - No credentials required in code
   - Suitable for Azure production environments
   - Supports both system-assigned and user-assigned identities

### Important Authentication Notes

- **ActiveDirectoryPassword Authentication**: Due to ODBC driver limitations with SQLAlchemy URL parsing, we use a custom connection creator function that builds the ODBC connection string directly.
- **Username Format**: Use full email format (user@domain.com) for Azure AD authentication.
- **ODBC Driver**: Requires ODBC Driver 18 for SQL Server for proper Azure AD support.
- **Connection Creator**: For ActiveDirectoryPassword, the system bypasses SQLAlchemy's URL parsing and uses a custom pyodbc connection function.

## Running Scripts

### Prerequisites
Ensure your virtual environment is activated and dependencies are installed:
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### Environment Setup
Make sure your `.env` file is properly configured with database connection details:
```env
DATABASE_URL=your_connection_string
# or individual components:
DB_SERVER=your_server
DB_NAME=CMSDEVB
DB_DRIVER=ODBC Driver 18 for SQL Server
```

### Running Individual Scripts
```bash
# From project root
cd scripts

# Run specific script
python find_classification_tables.py
python inspect_tables.py
python inspect_pdc_classifications.py
```

## Script Dependencies

All scripts depend on:
- `database.config` - Database connection configuration
- `sqlalchemy` - Database ORM and inspection
- `.env` file - Database credentials
- Active database connection to CMSDEVB

## Output Files

Some scripts may generate output files:
- Model code suggestions (printed to console)
- Temporary analysis files
- Database structure documentation

## Troubleshooting

### Common Issues

**Import Errors**:
- Ensure you're running from the correct directory
- Check that project root is in Python path
- Verify virtual environment is activated

**Database Connection Issues**:
- Verify `.env` file configuration
- Check network connectivity to database server
- Ensure proper authentication credentials

**Permission Issues**:
- Verify database user has SELECT permissions on system tables
- Check if user can access table metadata

### Getting Help

If scripts fail:
1. Check database connectivity first
2. Verify environment variables are set
3. Check console output for specific error messages
4. Ensure all dependencies are installed

## Adding New Scripts

When adding new utility scripts:
1. Place them in the `scripts/` directory
2. Add proper project root path handling:
   ```python
   # Add the project root to Python path (go up one level from scripts/)
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```
3. Import required modules after path setup
4. Add documentation to this README
5. Follow existing naming conventions