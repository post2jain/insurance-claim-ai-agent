from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from app.models.schemas import Claim, ClaimCreate, ClaimUpdate
from app.models.enums import ClaimStatus
from app.repositories.claim_repository import ClaimRepository
from app.services.ai_service import AIService
from app.services.video_service import VideoService

class ClaimsService:
    def __init__(
        self,
        claim_repository: ClaimRepository,
        ai_service: AIService,
        video_service: VideoService
    ):
        self.claim_repository = claim_repository
        self.ai_service = ai_service
        self.video_service = video_service
    
    def create_claim(self, claim_data: ClaimCreate) -> Claim:
        """Create a new claim."""
        claim = self.claim_repository.create(claim_data.dict())
        
        # Generate AI suggestions for the new claim
        self.ai_service.generate_suggestions(claim.id)
        
        return claim
    
    def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        """Get a claim by ID."""
        return self.claim_repository.get(claim_id)
    
    def get_claims(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ClaimStatus] = None,
        policy_number: Optional[str] = None,
        policyholder_name: Optional[str] = None
    ) -> List[Claim]:
        """Get claims with optional filters."""
        return self.claim_repository.get_with_filters(
            skip=skip,
            limit=limit,
            status=status,
            policy_number=policy_number,
            policyholder_name=policyholder_name
        )
    
    def update_claim(self, claim_id: UUID, claim_data: ClaimUpdate) -> Optional[Claim]:
        """Update a claim."""
        return self.claim_repository.update(claim_id, claim_data.dict(exclude_unset=True))
    
    def delete_claim(self, claim_id: UUID) -> bool:
        """Delete a claim."""
        return self.claim_repository.delete(claim_id)
    
    def update_claim_status(self, claim_id: UUID, status: ClaimStatus) -> Optional[Claim]:
        """Update claim status."""
        return self.claim_repository.update_status(claim_id, status)
    
    def get_claims_with_video_analysis(self) -> List[Claim]:
        """Get claims that have video analysis results."""
        return self.claim_repository.get_with_video_analysis()
    
    def get_recent_claims(self, days: int = 7) -> List[Claim]:
        """Get claims created within the last N days."""
        return self.claim_repository.get_recent_claims(days)
    
    def get_claim_metrics(self) -> Dict[str, Any]:
        """Get claim metrics."""
        return self.claim_repository.get_metrics()
    
    def process_video_upload(self, claim_id: UUID, video_file: bytes) -> Dict[str, Any]:
        """Process a video upload for a claim."""
        # Upload and analyze video
        video_analysis = self.video_service.analyze_video(video_file)
        
        # Update claim with video analysis results
        self.claim_repository.update(claim_id, {
            "video_analysis": video_analysis,
            "has_video": True
        })
        
        # Generate new suggestions based on video analysis
        self.ai_service.generate_suggestions(claim_id)
        
        return video_analysis 