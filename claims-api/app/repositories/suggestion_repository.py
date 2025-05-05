from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.schemas import AISuggestion
from app.models.enums import SuggestionStatus, SuggestionType
from .base import BaseRepository

class SuggestionRepository(BaseRepository[AISuggestion]):
    def __init__(self, db: Session):
        super().__init__(AISuggestion, db)
    
    def get_by_claim(self, claim_id: UUID) -> List[AISuggestion]:
        """Get all suggestions for a specific claim."""
        return self.db.query(self.model).filter(
            self.model.claim_id == claim_id
        ).order_by(self.model.created_at.desc()).all()
    
    def get_by_status(self, status: SuggestionStatus) -> List[AISuggestion]:
        """Get all suggestions with a specific status."""
        return self.db.query(self.model).filter(
            self.model.status == status
        ).all()
    
    def get_by_type(self, type: SuggestionType) -> List[AISuggestion]:
        """Get all suggestions of a specific type."""
        return self.db.query(self.model).filter(
            self.model.type == type
        ).all()
    
    def get_with_filters(
        self,
        claim_id: Optional[UUID] = None,
        status: Optional[SuggestionStatus] = None,
        type: Optional[SuggestionType] = None
    ) -> List[AISuggestion]:
        """Get suggestions with multiple filters."""
        query = self.db.query(self.model)
        
        if claim_id:
            query = query.filter(self.model.claim_id == claim_id)
        if status:
            query = query.filter(self.model.status == status)
        if type:
            query = query.filter(self.model.type == type)
        
        return query.order_by(self.model.created_at.desc()).all()
    
    def update_status(
        self,
        suggestion_id: UUID,
        status: SuggestionStatus,
        reviewer_id: UUID,
        reviewer_notes: Optional[str] = None,
        modified_action: Optional[str] = None
    ) -> Optional[AISuggestion]:
        """Update suggestion status and review information."""
        update_data = {
            "status": status,
            "reviewer_id": reviewer_id,
            "reviewer_notes": reviewer_notes,
            "reviewed_at": func.now()
        }
        if modified_action:
            update_data["suggested_action"] = modified_action
        
        return self.update(suggestion_id, update_data)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get suggestion metrics."""
        total = self.db.query(func.count(self.model.id)).scalar()
        
        accepted = self.db.query(func.count(self.model.id)).filter(
            self.model.status == SuggestionStatus.ACCEPTED
        ).scalar()
        
        rejected = self.db.query(func.count(self.model.id)).filter(
            self.model.status == SuggestionStatus.REJECTED
        ).scalar()
        
        modified = self.db.query(func.count(self.model.id)).filter(
            self.model.status == SuggestionStatus.MODIFIED
        ).scalar()
        
        suggestions_by_type = self.db.query(
            self.model.type,
            func.count(self.model.id)
        ).group_by(self.model.type).all()
        
        return {
            "total_suggestions": total,
            "acceptance_rate": accepted / total if total > 0 else 0,
            "rejection_rate": rejected / total if total > 0 else 0,
            "modification_rate": modified / total if total > 0 else 0,
            "suggestions_by_type": suggestions_by_type
        }
    
    def get_high_confidence_suggestions(self, threshold: float = 0.8) -> List[AISuggestion]:
        """Get suggestions with confidence score above threshold."""
        return self.db.query(self.model).filter(
            self.model.confidence_score >= threshold
        ).all()
    
    def get_pending_suggestions(self) -> List[AISuggestion]:
        """Get all pending suggestions."""
        return self.get_by_status(SuggestionStatus.PENDING) 