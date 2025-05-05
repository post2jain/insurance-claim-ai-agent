from datetime import datetime
from typing import List, Optional, TypedDict
from uuid import UUID

from .enums import ClaimStatus, SuggestionStatus, SuggestionType
from .types import ClaimId, SuggestionId, JsonDict


class Address(TypedDict):
    street: str
    city: str
    state: str
    zipcode: str
    country: str


class ClaimItem(TypedDict):
    name: str
    description: str
    category: str
    estimated_value: float
    purchase_date: Optional[datetime]
    replacement_cost: Optional[float]


class ClaimBase(TypedDict):
    policy_number: str
    policyholder_name: str
    date_of_loss: datetime
    description: str
    total_amount: float
    incident_location: Address
    items: List[ClaimItem]


class ClaimCreate(ClaimBase):
    pass


class Claim(ClaimBase):
    id: ClaimId
    status: ClaimStatus
    created_at: datetime
    updated_at: datetime
    assigned_adjuster: Optional[str]
    supporting_documents: Optional[List[str]]
    video_evidence: Optional[str]
    ml_processing_results: Optional[JsonDict]


class AISuggestion(TypedDict):
    id: SuggestionId
    claim_id: ClaimId
    type: SuggestionType
    description: str
    confidence_score: float  # 0.0 to 1.0
    ai_explanation: str
    suggested_action: JsonDict
    status: SuggestionStatus
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewer_id: Optional[str]
    reviewer_notes: Optional[str]
    model_version: str


# Review feedback model
class SuggestionReview(TypedDict):
    suggestion_id: SuggestionId
    status: SuggestionStatus
    reviewer_id: str
    reviewer_notes: Optional[str]
    modified_action: Optional[JsonDict]
