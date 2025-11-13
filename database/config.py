"""
Database configuration for Azure SQL Server connection using SQLAlchemy ORM.
Supports both SQL authentication and Managed Identity authentication.
"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """
    Database configuration class for Azure SQL Server.
    Supports both SQL authentication and Managed Identity authentication.
    """
    
    def __init__(self):
        self.driver = os.getenv('AZURE_SQL_DRIVER', 'ODBC Driver 18 for SQL Server')
        self.server = os.getenv('AZURE_SQL_SERVER')
        self.database = os.getenv('AZURE_SQL_DATABASE')
        self.username = os.getenv('AZURE_SQL_USERNAME')
        self.password = os.getenv('AZURE_SQL_PASSWORD')
        self.port = os.getenv('AZURE_SQL_PORT', '1433')
        
        # Authentication method: 'sql' or 'managed_identity'
        self.auth_method = os.getenv('AZURE_SQL_AUTH_METHOD', 'sql').lower()
        
        # SQL Authentication settings
        self.authentication = os.getenv('AZURE_SQL_AUTHENTICATION', 'ActiveDirectoryPassword')
        
        # Managed Identity settings
        self.managed_identity_client_id = os.getenv('AZURE_CLIENT_ID')  # Optional: User-assigned MI
        
    def _get_sql_auth_connection_string(self) -> str:
        """Generate connection string for SQL authentication."""
        if not all([self.server, self.database, self.username, self.password]):
            raise ValueError(
                "Missing required parameters for SQL authentication. "
                "Required: AZURE_SQL_SERVER, AZURE_SQL_DATABASE, AZURE_SQL_USERNAME, AZURE_SQL_PASSWORD"
            )
        
        # URL encode credentials to handle special characters
        encoded_username = quote_plus(self.username)
        encoded_password = quote_plus(self.password)
        
        # Handle different authentication methods
        if self.authentication == 'SqlPassword':
            # Use traditional SQL authentication format
            connection_string = (
                f"mssql+pyodbc://{encoded_username}:{encoded_password}@"
                f"{self.server}:{self.port}/{self.database}"
                f"?driver={quote_plus(self.driver)}&Encrypt=yes&TrustServerCertificate=no"
            )
        elif self.authentication in ['ActiveDirectoryPassword', 'ActiveDirectoryIntegrated']:
            # Use a minimal connection string - all parameters will be in connect_args
            connection_string = "mssql+pyodbc:///"
        else:
            # For other authentication methods (like SQL Server authentication)
            connection_string = (
                f"mssql+pyodbc://{encoded_username}:{encoded_password}@{self.server}:{self.port}/{self.database}"
                f"?driver={quote_plus(self.driver)}&Encrypt=yes&TrustServerCertificate=no"
            )
            
        return connection_string
    
    def _get_managed_identity_connection_string(self) -> str:
        """Generate connection string for Managed Identity authentication."""
        if not all([self.server, self.database]):
            raise ValueError(
                "Missing required parameters for Managed Identity authentication. "
                "Required: AZURE_SQL_SERVER, AZURE_SQL_DATABASE"
            )
        
        # Base connection string without credentials
        connection_string = (
            f"mssql+pyodbc://@{self.server}:{self.port}/{self.database}"
            f"?driver={quote_plus(self.driver)}&Authentication=ActiveDirectoryMsi&Encrypt=yes&TrustServerCertificate=no"
        )
        
        # Add client ID for user-assigned managed identity if provided
        if self.managed_identity_client_id:
            connection_string += f"&UID={self.managed_identity_client_id}"
        
        return connection_string
        
    def get_connection_string(self) -> str:
        """
        Generate SQLAlchemy connection string based on authentication method.
        
        Returns:
            str: Connection string for the configured authentication method
            
        Raises:
            ValueError: If authentication method is invalid or required parameters are missing
        """
        if self.auth_method == 'sql':
            print(f"Using SQL authentication for database: {self.database}")
            return self._get_sql_auth_connection_string()
        elif self.auth_method == 'managed_identity':
            print(f"Using Managed Identity authentication for database: {self.database}")
            if self.managed_identity_client_id:
                print(f"Using User-Assigned Managed Identity: {self.managed_identity_client_id}")
            else:
                print("Using System-Assigned Managed Identity")
            return self._get_managed_identity_connection_string()
        else:
            raise ValueError(
                f"Invalid authentication method: {self.auth_method}. "
                "Supported methods: 'sql', 'managed_identity'"
            )

# Global variables for lazy initialization
_engine = None
_SessionLocal = None
_db_config = None

def get_engine():
    """Get or create the SQLAlchemy engine with lazy initialization."""
    global _engine, _db_config
    
    if _engine is None:
        import logging
        
        # Create database configuration instance
        _db_config = DatabaseConfig()
        
        # Log the configuration being used
        logging.info(f"🚀 Initializing database engine with auth_method: {_db_config.auth_method}")
        
        # Create SQLAlchemy engine with special handling for all Azure AD auth methods
        if (_db_config.auth_method == 'sql' and _db_config.authentication == 'ActiveDirectoryPassword') or \
           (_db_config.auth_method == 'managed_identity'):
            
            logging.info(f"🔧 Using custom connection creator for auth_method: {_db_config.auth_method}")
            
            # Create a custom connection function that builds the ODBC connection string properly
            def create_connection():
                import pyodbc
                import logging
                
                if _db_config.auth_method == 'sql':
                    # SQL authentication with ActiveDirectoryPassword
                    connection_string = (
                        f"DRIVER={{{_db_config.driver}}};"
                        f"SERVER={_db_config.server};"
                        f"DATABASE={_db_config.database};"
                        f"Authentication={_db_config.authentication};"
                        f"UID={_db_config.username};"
                        f"PWD={_db_config.password};"
                        "Encrypt=yes;"
                        "TrustServerCertificate=no;"
                    )
                    # Log connection string (without password for security)
                    safe_connection_string = connection_string.replace(f"PWD={_db_config.password};", "PWD=***;")
                    logging.info(f"🔗 Using SQL Authentication Connection String: {safe_connection_string}")
                else:
                    # Managed Identity authentication
                    connection_string = (
                        f"DRIVER={{{_db_config.driver}}};"
                        f"SERVER={_db_config.server};"
                        f"DATABASE={_db_config.database};"
                        "Authentication=ActiveDirectoryMsi;"
                        "Encrypt=yes;"
                        "TrustServerCertificate=no;"
                    )
                    
                    # Add client ID for user-assigned managed identity if provided
                    if _db_config.managed_identity_client_id:
                        connection_string += f"UID={_db_config.managed_identity_client_id};"
                    
                    # Log the full connection string for managed identity (no sensitive data)
                    logging.info(f"🔗 Using Managed Identity Connection String: {connection_string}")
                
                # Log auth method and configuration
                logging.info(f"🔧 Database Auth Method: {_db_config.auth_method}")
                if _db_config.auth_method == 'sql':
                    logging.info(f"🔧 Authentication Type: {_db_config.authentication}")
                else:
                    logging.info(f"🔧 Authentication Type: ActiveDirectoryMsi (Managed Identity)")
                
                return pyodbc.connect(connection_string)
            
            _engine = create_engine(
                "mssql+pyodbc://",  # Dummy connection string
                echo=True,  # Set to False in production
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                creator=create_connection
            )
        else:
            # Standard SQLAlchemy connection (for other auth methods)
            connection_string = _db_config.get_connection_string()
            logging.info(f"🔧 Using standard SQLAlchemy connection: {connection_string}")
            _engine = create_engine(
                connection_string,
                echo=True,  # Set to False in production
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
    
    return _engine

def get_session_local():
    """Get or create the SessionLocal class with lazy initialization."""
    global _SessionLocal
    
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    
    return _SessionLocal

def get_db():
    """Dependency to get database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
