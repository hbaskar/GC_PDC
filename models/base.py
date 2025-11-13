"""
Base configuration for SQLAlchemy models.
This module provides the shared Base class and common imports.
"""
from sqlalchemy.ext.declarative import declarative_base

# Create the Base class that all models will inherit from
Base = declarative_base()

# Common imports that models will need
__all__ = ['Base']
