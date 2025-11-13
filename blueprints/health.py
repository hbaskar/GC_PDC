"""
Health and Diagnostic API Blueprint
Contains health check and diagnostic endpoints.
"""
import azure.functions as func
import logging
import os
from datetime import datetime
from sqlalchemy import text

# Import dependencies
from database.config import get_db, DatabaseConfig, get_engine
from schemas.classification_schemas import ErrorResponse

# Create blueprint
bp = func.Blueprint()

def create_error_response(message: str, status_code: int, detail: str = None) -> func.HttpResponse:
    """Create standardized error response."""
    error_response = ErrorResponse(
        error=message,
        detail=detail,
        status_code=status_code
    )
    return func.HttpResponse(
        error_response.model_dump_json(),
        status_code=status_code,
        mimetype="application/json"
    )

def create_success_response(data: dict, status_code: int = 200) -> func.HttpResponse:
    """Create standardized success response."""
    import json
    return func.HttpResponse(
        json.dumps(data, default=str),
        status_code=status_code,
        mimetype="application/json"
    )

@bp.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Basic health check endpoint."""
    try:
        # Test database connection
        db = next(get_db())
        
        # Simple query to test connection
        db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "PDC Classification API",
            "version": "1.0.0",
            "database": "connected"
        }
        
        return create_success_response(health_data)
        
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        
        health_data = {
            "status": "unhealthy", 
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "PDC Classification API",
            "version": "1.0.0",
            "database": "disconnected",
            "error": str(e)
        }
        
        return create_success_response(health_data, 503)

@bp.route(route="health/detailed", methods=["GET"])
def detailed_health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Detailed health check with component status."""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "PDC Classification API",
            "version": "1.0.0",
            "components": {}
        }
        
        # Test database connection
        try:
            db = next(get_db())
            result = db.execute(text("SELECT @@VERSION")).fetchone()
            db.close()
            
            health_data["components"]["database"] = {
                "status": "healthy",
                "server_version": result[0] if result else "unknown",
                "connection": "active"
            }
        except Exception as db_error:
            health_data["components"]["database"] = {
                "status": "unhealthy",
                "error": str(db_error),
                "connection": "failed"
            }
            health_data["status"] = "degraded"
        
        # Test environment variables
        required_env_vars = ["AZURE_SQL_SERVER", "AZURE_SQL_DATABASE", "AZURE_SQL_USERNAME"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        health_data["components"]["environment"] = {
            "status": "healthy" if not missing_vars else "unhealthy",
            "missing_variables": missing_vars
        }
        
        if missing_vars:
            health_data["status"] = "degraded"
        
        # Overall status
        status_code = 200 if health_data["status"] == "healthy" else 503
        
        return create_success_response(health_data, status_code)
        
    except Exception as e:
        logging.error(f"Detailed health check failed: {str(e)}")
        return create_error_response("Health check failed", 500, str(e))

@bp.route(route="diagnostic", methods=["GET"])
def diagnostic_info(req: func.HttpRequest) -> func.HttpResponse:
    """Get diagnostic information about the system configuration."""
    try:
        diagnostic_info = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": {
                "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}",
                "platform": __import__('platform').system(),
                "architecture": __import__('platform').architecture()[0]
            },
            "configuration": {},
            "database_config": {},
            "engine_info": {}
        }
        
        # Environment variables (sanitized)
        env_vars = ["AZURE_SQL_SERVER", "AZURE_SQL_DATABASE", "AZURE_SQL_USERNAME", "AZURE_SQL_AUTH_METHOD", "AZURE_CLIENT_ID"]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Sanitize sensitive info
                if var in ["AZURE_SQL_PASSWORD", "SQL_CONNECTION_STRING"]:
                    diagnostic_info["configuration"][var] = "***"
                elif "PASSWORD" in var or "SECRET" in var or "KEY" in var:
                    diagnostic_info["configuration"][var] = "***"
                else:
                    diagnostic_info["configuration"][var] = value
            else:
                diagnostic_info["configuration"][var] = None
        
        # Database configuration details
        try:
            config = DatabaseConfig()
            diagnostic_info["database_config"] = {
                "auth_method": config.auth_method,
                "server": config.server,
                "database": config.database,
                "driver": config.driver,
                "encrypt": getattr(config, 'encrypt', None),
                "trust_server_certificate": getattr(config, 'trust_server_certificate', None)
            }
            
            # Determine connection creator info
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
        
        return create_success_response(diagnostic_info)
        
    except Exception as e:
        logging.error(f"Diagnostic endpoint failed: {str(e)}")
        return create_error_response("Diagnostic failed", 500, str(e))
