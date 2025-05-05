from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.claim_repository import ClaimRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.ai_service import AIService
from app.services.video_service import VideoService
from app.services.claims_service import ClaimsService
from app.services.suggestions_service import SuggestionsService

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_claim_repository(db: Session = Depends(get_db)) -> ClaimRepository:
    """Get claim repository instance."""
    return ClaimRepository(db)

def get_suggestion_repository(db: Session = Depends(get_db)) -> SuggestionRepository:
    """Get suggestion repository instance."""
    return SuggestionRepository(db)

def get_ai_service() -> AIService:
    """Get AI service instance."""
    return AIService()

def get_video_service() -> VideoService:
    """Get video service instance."""
    return VideoService()

def get_claims_service(
    claim_repository: ClaimRepository = Depends(get_claim_repository),
    ai_service: AIService = Depends(get_ai_service),
    video_service: VideoService = Depends(get_video_service)
) -> ClaimsService:
    """Get claims service instance."""
    return ClaimsService(claim_repository, ai_service, video_service)

def get_suggestions_service(
    suggestion_repository: SuggestionRepository = Depends(get_suggestion_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> SuggestionsService:
    """Get suggestions service instance."""
    return SuggestionsService(suggestion_repository, ai_service) 