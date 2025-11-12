import azure.functions as func
import logging

# Import blueprints
from blueprints.classifications import bp as classifications_bp
from blueprints.lookups import bp as lookups_bp  
from blueprints.health import bp as health_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Register blueprints
app.register_blueprint(classifications_bp)
app.register_blueprint(lookups_bp)
app.register_blueprint(health_bp)