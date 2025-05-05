from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.schemas import AISuggestion, SuggestionCreate, SuggestionUpdate
from app.models.enums import SuggestionStatus, SuggestionType
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.ai_service import AIService

class SuggestionsService:
    def __init__(
        self,
        suggestion_repository: SuggestionRepository,
        ai_service: AIService
    ):
        self.suggestion_repository = suggestion_repository
        self.ai_service = ai_service
    
    def create_suggestion(self, suggestion_data: SuggestionCreate) -> AISuggestion:
        """Create a new suggestion."""
        return self.suggestion_repository.create(suggestion_data.dict())
    
    def get_suggestion(self, suggestion_id: UUID) -> Optional[AISuggestion]:
        """Get a suggestion by ID."""
        return self.suggestion_repository.get(suggestion_id)
    
    def get_suggestions(
        self,
        claim_id: Optional[UUID] = None,
        status: Optional[SuggestionStatus] = None,
        type: Optional[SuggestionType] = None
    ) -> List[AISuggestion]:
        """Get suggestions with optional filters."""
        return self.suggestion_repository.get_with_filters(
            claim_id=claim_id,
            status=status,
            type=type
        )
    
    def update_suggestion(
        self,
        suggestion_id: UUID,
        suggestion_data: SuggestionUpdate
    ) -> Optional[AISuggestion]:
        """Update a suggestion."""
        return self.suggestion_repository.update(
            suggestion_id,
            suggestion_data.dict(exclude_unset=True)
        )
    
    def delete_suggestion(self, suggestion_id: UUID) -> bool:
        """Delete a suggestion."""
        return self.suggestion_repository.delete(suggestion_id)
    
    def update_suggestion_status(
        self,
        suggestion_id: UUID,
        status: SuggestionStatus,
        reviewer_id: UUID,
        reviewer_notes: Optional[str] = None,
        modified_action: Optional[str] = None
    ) -> Optional[AISuggestion]:
        """Update suggestion status and review information."""
        return self.suggestion_repository.update_status(
            suggestion_id,
            status,
            reviewer_id,
            reviewer_notes,
            modified_action
        )
    
    def get_suggestion_metrics(self) -> Dict[str, Any]:
        """Get suggestion metrics."""
        return self.suggestion_repository.get_metrics()
    
    def get_high_confidence_suggestions(self, threshold: float = 0.8) -> List[AISuggestion]:
        """Get suggestions with confidence score above threshold."""
        return self.suggestion_repository.get_high_confidence_suggestions(threshold)
    
    def get_pending_suggestions(self) -> List[AISuggestion]:
        """Get all pending suggestions."""
        return self.suggestion_repository.get_pending_suggestions()
    
    def regenerate_suggestions(self, claim_id: UUID) -> List[AISuggestion]:
        """Regenerate suggestions for a claim using AI."""
        # Delete existing suggestions for the claim
        existing_suggestions = self.suggestion_repository.get_by_claim(claim_id)
        for suggestion in existing_suggestions:
            self.suggestion_repository.delete(suggestion.id)
        
        # Generate new suggestions
        return self.ai_service.generate_suggestions(claim_id) 