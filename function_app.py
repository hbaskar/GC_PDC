
import azure.functions as func
import logging

import models  # Ensure all models are registered for SQLAlchemy
from database.config import get_engine, DatabaseConfig

# Startup check: print database URL and test connection
db_config = DatabaseConfig()
print(f"[Startup] Using database URL: {db_config.get_connection_string()}")
try:
	engine = get_engine()
	with engine.connect() as conn:
		print("[Startup] Successfully connected to the database.")
except Exception as e:
	print(f"[Startup] Database connection failed: {e}")

# Import blueprints
from blueprints.classifications import bp as classifications_bp
from blueprints.lookups import bp as lookups_bp  
from blueprints.health import bp as health_bp
from blueprints.retention_policies import bp as retention_policies_bp
from blueprints.libraries import bp as libraries_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Register blueprints
app.register_blueprint(classifications_bp)
app.register_blueprint(lookups_bp)
app.register_blueprint(health_bp)
app.register_blueprint(retention_policies_bp)
app.register_blueprint(libraries_bp)
