from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.schemas import Claim
from app.models.enums import ClaimStatus
from .base import BaseRepository

class ClaimRepository(BaseRepository[Claim]):
    def __init__(self, db: Session):
        super().__init__(Claim, db)
    
    def get_by_policy_number(self, policy_number: str) -> List[Claim]:
        """Get all claims for a specific policy number."""
        return self.db.query(self.model).filter(
            self.model.policy_number == policy_number
        ).all()
    
    def get_by_status(self, status: ClaimStatus) -> List[Claim]:
        """Get all claims with a specific status."""
        return self.db.query(self.model).filter(
            self.model.status == status
        ).all()
    
    def get_by_policyholder(self, name: str) -> List[Claim]:
        """Get all claims for a specific policyholder."""
        return self.db.query(self.model).filter(
            self.model.policyholder_name.ilike(f"%{name}%")
        ).all()
    
    def get_with_filters(
        self,
        status: Optional[ClaimStatus] = None,
        policyholder_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Claim]:
        """Get claims with multiple filters."""
        query = self.db.query(self.model)
        
        if status:
            query = query.filter(self.model.status == status)
        if policyholder_name:
            query = query.filter(self.model.policyholder_name.ilike(f"%{policyholder_name}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def update_status(self, claim_id: UUID, status: ClaimStatus) -> Optional[Claim]:
        """Update claim status."""
        return self.update(claim_id, {"status": status})
    
    def get_with_video_analysis(self) -> List[Claim]:
        """Get all claims that have video analysis results."""
        return self.db.query(self.model).filter(
            self.model.ml_processing_results.isnot(None)
        ).all()
    
    def get_recent_claims(self, days: int = 30) -> List[Claim]:
        """Get claims created in the last N days."""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(self.model).filter(
            self.model.created_at >= cutoff_date
        ).all() 