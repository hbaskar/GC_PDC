import azure.functions as func
import logging
import json
import os
from datetime import datetime

def diagnostic_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Diagnostic endpoint to debug managed identity configuration in Azure.
    Access via: /api/diagnostic
    """
    try:
        diagnostic_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment_variables": {
                "AZURE_SQL_AUTH_METHOD": os.environ.get('AZURE_SQL_AUTH_METHOD', 'NOT SET'),
                "AZURE_SQL_SERVER": os.environ.get('AZURE_SQL_SERVER', 'NOT SET'),
                "AZURE_SQL_DATABASE": os.environ.get('AZURE_SQL_DATABASE', 'NOT SET'),
                "AZURE_SQL_DRIVER": os.environ.get('AZURE_SQL_DRIVER', 'NOT SET'),
                "AZURE_SQL_PORT": os.environ.get('AZURE_SQL_PORT', 'NOT SET'),
                "AZURE_SQL_MANAGED_IDENTITY_CLIENT_ID": os.environ.get('AZURE_SQL_MANAGED_IDENTITY_CLIENT_ID', 'NOT SET'),
                
                # Check if any old variables are still set
                "AZURE_SQL_USERNAME": "SET" if os.environ.get('AZURE_SQL_USERNAME') else 'NOT SET',
                "AZURE_SQL_PASSWORD": "SET" if os.environ.get('AZURE_SQL_PASSWORD') else 'NOT SET',
                "AZURE_SQL_AUTHENTICATION": os.environ.get('AZURE_SQL_AUTHENTICATION', 'NOT SET'),
            },
            "database_config": None,
            "engine_info": None,
            "connection_test": None
        }
        
        # Test database configuration creation
        try:
            from database.config import DatabaseConfig
            
            # Clear any cached config first
            import database.config
            database.config._db_config = None
            database.config._engine = None
            database.config._SessionLocal = None
            
            config = DatabaseConfig()
            diagnostic_info["database_config"] = {
                "auth_method": config.auth_method,
                "server": config.server,
                "database": config.database,
                "driver": config.driver,
                "managed_identity_client_id": config.managed_identity_client_id,
                "port": config.port,
            }
            
            # Test connection string generation
            connection_string = config.get_connection_string()
            diagnostic_info["database_config"]["connection_string"] = connection_string
            
            # Check engine creation logic
            sql_condition = (config.auth_method == 'sql' and getattr(config, 'authentication', None) == 'ActiveDirectoryPassword')
            mi_condition = (config.auth_method == 'managed_identity')
            combined_condition = sql_condition or mi_condition
            
            diagnostic_info["engine_info"] = {
                "sql_condition": sql_condition,
                "mi_condition": mi_condition,
                "combined_condition": combined_condition,
                "will_use_custom_creator": combined_condition
            }
            
        except Exception as e:
            diagnostic_info["database_config"] = f"ERROR: {str(e)}"
            logging.error(f"Database config creation failed: {str(e)}")
        
        # Test actual engine creation
        try:
            from database.config import get_engine
            
            engine = get_engine()
            has_custom_creator = hasattr(engine.pool, '_creator')
            
            diagnostic_info["engine_info"] = {
                **diagnostic_info.get("engine_info", {}),
                "engine_type": str(type(engine)),
                "has_custom_creator": has_custom_creator,
            }
            
        except Exception as e:
            diagnostic_info["engine_info"] = {
                **diagnostic_info.get("engine_info", {}),
                "engine_creation_error": str(e)
            }
            logging.error(f"Engine creation failed: {str(e)}")
        
        # Test database connection
        try:
            from database.config import get_db
            
            with get_db() as db:
                diagnostic_info["connection_test"] = {
                    "session_creation": "SUCCESS",
                    "session_type": str(type(db))
                }
            
        except Exception as e:
            diagnostic_info["connection_test"] = {
                "session_creation": "FAILED", 
                "error": str(e)
            }
            logging.error(f"Database connection test failed: {str(e)}")
        
        return func.HttpResponse(
            json.dumps(diagnostic_info, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Diagnostic endpoint failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Diagnostic failed",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }),
            status_code=500,
            mimetype="application/json"
        )
