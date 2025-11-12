"""
CRUD operations for PDC Classifications.
Based on actual database table structure from CMSDEVDB.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
from models import PDCClassification
from schemas.pdc_schemas import PDCClassificationCreate, PDCClassificationUpdate

class PDCClassificationCRUD:
    """CRUD operations for PDC Classifications."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, classification_data: PDCClassificationCreate) -> PDCClassification:
        """Create a new PDC Classification."""
        db_classification = PDCClassification(**classification_data.dict())
        self.db.add(db_classification)
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def get_by_id(self, classification_id: int, include_deleted: bool = False) -> Optional[PDCClassification]:
        """Get PDC Classification by ID."""
        query = self.db.query(PDCClassification).filter(
            PDCClassification.classification_id == classification_id
        )
        
        if not include_deleted:
            query = query.filter(PDCClassification.is_deleted == False)
        
        return query.first()
    
    def get_by_code(self, code: str, include_deleted: bool = False) -> Optional[PDCClassification]:
        """Get PDC Classification by code."""
        query = self.db.query(PDCClassification).filter(
            PDCClassification.code == code
        )
        
        if not include_deleted:
            query = query.filter(PDCClassification.is_deleted == False)
        
        return query.first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        classification_level: Optional[str] = None,
        organization_id: Optional[int] = None,
        sensitivity_rating: Optional[int] = None,
        media_type: Optional[str] = None,
        file_type: Optional[str] = None,
        search: Optional[str] = None,
        include_deleted: bool = False
    ) -> tuple[List[PDCClassification], int]:
        """Get all PDC Classifications with filtering and pagination."""
        query = self.db.query(PDCClassification)
        
        # Exclude deleted records by default
        if not include_deleted:
            query = query.filter(PDCClassification.is_deleted == False)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(PDCClassification.is_active == is_active)
        
        if classification_level:
            query = query.filter(PDCClassification.classification_level == classification_level)
        
        if organization_id:
            query = query.filter(PDCClassification.organization_id == organization_id)
        
        if sensitivity_rating:
            query = query.filter(PDCClassification.sensitivity_rating == sensitivity_rating)
        
        if media_type:
            query = query.filter(PDCClassification.media_type == media_type)
        
        if file_type:
            query = query.filter(PDCClassification.file_type == file_type)
        
        if search:
            search_filter = or_(
                PDCClassification.name.ilike(f"%{search}%"),
                PDCClassification.description.ilike(f"%{search}%"),
                PDCClassification.code.ilike(f"%{search}%"),
                PDCClassification.series.ilike(f"%{search}%"),
                PDCClassification.classification_purpose.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        classifications = query.order_by(PDCClassification.name).offset(skip).limit(limit).all()
        
        return classifications, total
    
    def update(self, classification_id: int, classification_data: PDCClassificationUpdate) -> Optional[PDCClassification]:
        """Update a PDC Classification."""
        db_classification = self.get_by_id(classification_id)
        if not db_classification:
            return None
        
        # Update only provided fields
        update_data = classification_data.dict(exclude_unset=True)
        
        # Set modified timestamp
        update_data['modified_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_classification, field, value)
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def delete(self, classification_id: int) -> bool:
        """Hard delete a PDC Classification."""
        db_classification = self.get_by_id(classification_id, include_deleted=True)
        if not db_classification:
            return False
        
        self.db.delete(db_classification)
        self.db.commit()
        return True
    
    def soft_delete(self, classification_id: int, deleted_by: Optional[str] = None) -> Optional[PDCClassification]:
        """Soft delete a PDC Classification by setting is_deleted to True."""
        db_classification = self.get_by_id(classification_id)
        if not db_classification:
            return None
        
        # Set deletion fields
        db_classification.is_deleted = True
        db_classification.deleted_at = datetime.utcnow()
        db_classification.deleted_by = deleted_by
        db_classification.modified_at = datetime.utcnow()
        db_classification.modified_by = deleted_by
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def restore(self, classification_id: int, restored_by: Optional[str] = None) -> Optional[PDCClassification]:
        """Restore a soft-deleted PDC Classification."""
        db_classification = self.get_by_id(classification_id, include_deleted=True)
        if not db_classification or not db_classification.is_deleted:
            return None
        
        # Clear deletion fields
        db_classification.is_deleted = False
        db_classification.deleted_at = None
        db_classification.deleted_by = None
        db_classification.modified_at = datetime.utcnow()
        db_classification.modified_by = restored_by
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def get_classification_levels(self) -> List[str]:
        """Get all unique classification levels."""
        levels = self.db.query(PDCClassification.classification_level).distinct().filter(
            and_(
                PDCClassification.classification_level.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [level[0] for level in levels if level[0]]
    
    def get_media_types(self) -> List[str]:
        """Get all unique media types."""
        media_types = self.db.query(PDCClassification.media_type).distinct().filter(
            and_(
                PDCClassification.media_type.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [media_type[0] for media_type in media_types if media_type[0]]
    
    def get_file_types(self) -> List[str]:
        """Get all unique file types."""
        file_types = self.db.query(PDCClassification.file_type).distinct().filter(
            and_(
                PDCClassification.file_type.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [file_type[0] for file_type in file_types if file_type[0]]
    
    def get_series(self) -> List[str]:
        """Get all unique series."""
        series = self.db.query(PDCClassification.series).distinct().filter(
            and_(
                PDCClassification.series.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [s[0] for s in series if s[0]]
    
    def get_by_organization(self, organization_id: int, is_active: Optional[bool] = None) -> List[PDCClassification]:
        """Get all classifications for a specific organization."""
        query = self.db.query(PDCClassification).filter(
            and_(
                PDCClassification.organization_id == organization_id,
                PDCClassification.is_deleted == False
            )
        )
        
        if is_active is not None:
            query = query.filter(PDCClassification.is_active == is_active)
        
        return query.order_by(PDCClassification.name).all()
    
    def get_by_sensitivity_rating(self, min_rating: int, max_rating: int = None) -> List[PDCClassification]:
        """Get classifications by sensitivity rating range."""
        query = self.db.query(PDCClassification).filter(
            and_(
                PDCClassification.sensitivity_rating >= min_rating,
                PDCClassification.is_deleted == False
            )
        )
        
        if max_rating:
            query = query.filter(PDCClassification.sensitivity_rating <= max_rating)
        
        return query.order_by(PDCClassification.sensitivity_rating.desc()).all()
    
    def update_last_accessed(self, classification_id: int, accessed_by: str) -> Optional[PDCClassification]:
        """Update last accessed information."""
        db_classification = self.get_by_id(classification_id)
        if not db_classification:
            return None
        
        db_classification.last_accessed_at = datetime.utcnow()
        db_classification.last_accessed_by = accessed_by
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification