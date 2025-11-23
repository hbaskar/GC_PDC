from sqlalchemy.orm import Session
from models.pdc_library import PDCLibrary
from models.pdc_classification import PDCClassification
from typing import Optional, List, Dict, Any
from datetime import datetime

class PDCLibraryService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: Optional[str] = None) -> PDCLibrary:
        library = PDCLibrary(name=name, description=description)
        self.db.add(library)
        self.db.commit()
        self.db.refresh(library)
        return library

    def get_by_id(self, library_id: int) -> Optional[PDCLibrary]:
        return self.db.query(PDCLibrary).filter(PDCLibrary.library_id == library_id).first()

    def get_all(self) -> List[PDCLibrary]:
        return self.db.query(PDCLibrary).all()

    def update(self, library_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[PDCLibrary]:
        library = self.get_by_id(library_id)
        if not library:
            return None
        if name:
            library.name = name
        if description:
            library.description = description
        library.modified_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(library)
        return library

    def delete(self, library_id: int) -> bool:
        library = self.get_by_id(library_id)
        if not library:
            return False
        self.db.delete(library)
        self.db.commit()
        return True

    def add_classification(self, library_id: int, classification_id: int) -> bool:
        library = self.get_by_id(library_id)
        classification = self.db.query(PDCClassification).filter(PDCClassification.classification_id == classification_id).first()
        if not library or not classification:
            return False
        library.classifications.append(classification)
        self.db.commit()
        return True

    def remove_classification(self, library_id: int, classification_id: int) -> bool:
        library = self.get_by_id(library_id)
        classification = self.db.query(PDCClassification).filter(PDCClassification.classification_id == classification_id).first()
        if not library or not classification:
            return False
        if classification in library.classifications:
            library.classifications.remove(classification)
            self.db.commit()
        return True
