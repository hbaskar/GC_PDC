

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class PDCLibrary(Base):
    __tablename__ = 'pdc_libraries'

    library_id = Column(Integer, primary_key=True, autoincrement=True)
    library_group_id = Column(Integer, nullable=False, default=0, server_default='0')
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False, default='system', server_default='system')
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(100), nullable=True)

    def to_dict(self):
        return {
            'library_id': self.library_id,
            'library_group_id': self.library_group_id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'created_by': self.created_by,
            'modified_at': self.modified_at,
            'modified_by': self.modified_by
        }

