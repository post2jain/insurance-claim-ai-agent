import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.models.schemas import Claim, AISuggestion
from app.models.enums import ClaimStatus, SuggestionStatus, SuggestionType
from app.repositories.claim_repository import ClaimRepository
from app.repositories.suggestion_repository import SuggestionRepository

def test_base_repository_crud(claim_repository: ClaimRepository, sample_claim_data: dict):
    # Test create
    claim = claim_repository.create(sample_claim_data)
    assert claim.id is not None
    assert claim.policy_number == sample_claim_data["policy_number"]
    
    # Test get
    retrieved_claim = claim_repository.get(claim.id)
    assert retrieved_claim is not None
    assert retrieved_claim.id == claim.id
    
    # Test update
    update_data = {"policyholder_name": "Jane Doe"}
    updated_claim = claim_repository.update(claim.id, update_data)
    assert updated_claim is not None
    assert updated_claim.policyholder_name == "Jane Doe"
    
    # Test delete
    assert claim_repository.delete(claim.id) is True
    assert claim_repository.get(claim.id) is None

def test_claim_repository_specific_methods(claim_repository: ClaimRepository):
    # Create test claims
    claim1 = claim_repository.create({
        "policy_number": "POL-1",
        "policyholder_name": "John Doe",
        "status": ClaimStatus.SUBMITTED
    })
    claim2 = claim_repository.create({
        "policy_number": "POL-1",
        "policyholder_name": "John Doe",
        "status": ClaimStatus.APPROVED
    })
    claim3 = claim_repository.create({
        "policy_number": "POL-2",
        "policyholder_name": "Jane Smith",
        "status": ClaimStatus.SUBMITTED
    })
    
    # Test get_by_policy_number
    policy_claims = claim_repository.get_by_policy_number("POL-1")
    assert len(policy_claims) == 2
    
    # Test get_by_status
    submitted_claims = claim_repository.get_by_status(ClaimStatus.SUBMITTED)
    assert len(submitted_claims) == 2
    
    # Test get_by_policyholder
    john_claims = claim_repository.get_by_policyholder("John")
    assert len(john_claims) == 2
    
    # Test get_with_filters
    filtered_claims = claim_repository.get_with_filters(
        status=ClaimStatus.SUBMITTED,
        policyholder_name="John"
    )
    assert len(filtered_claims) == 1
    
    # Test update_status
    updated_claim = claim_repository.update_status(claim1.id, ClaimStatus.APPROVED)
    assert updated_claim.status == ClaimStatus.APPROVED
    
    # Test get_recent_claims
    recent_claims = claim_repository.get_recent_claims(days=1)
    assert len(recent_claims) == 3

def test_suggestion_repository_specific_methods(
    suggestion_repository: SuggestionRepository,
    sample_suggestion_data: dict
):
    # Create test suggestions
    claim_id = uuid4()
    suggestion1 = suggestion_repository.create({
        **sample_suggestion_data,
        "claim_id": claim_id,
        "type": SuggestionType.DAMAGE_ASSESSMENT,
        "status": SuggestionStatus.PENDING
    })
    suggestion2 = suggestion_repository.create({
        **sample_suggestion_data,
        "claim_id": claim_id,
        "type": SuggestionType.FRAUD_DETECTION,
        "status": SuggestionStatus.ACCEPTED
    })
    suggestion3 = suggestion_repository.create({
        **sample_suggestion_data,
        "claim_id": uuid4(),
        "type": SuggestionType.DAMAGE_ASSESSMENT,
        "status": SuggestionStatus.PENDING
    })
    
    # Test get_by_claim
    claim_suggestions = suggestion_repository.get_by_claim(claim_id)
    assert len(claim_suggestions) == 2
    
    # Test get_by_status
    pending_suggestions = suggestion_repository.get_by_status(SuggestionStatus.PENDING)
    assert len(pending_suggestions) == 2
    
    # Test get_by_type
    damage_suggestions = suggestion_repository.get_by_type(SuggestionType.DAMAGE_ASSESSMENT)
    assert len(damage_suggestions) == 2
    
    # Test get_with_filters
    filtered_suggestions = suggestion_repository.get_with_filters(
        claim_id=claim_id,
        status=SuggestionStatus.PENDING,
        type=SuggestionType.DAMAGE_ASSESSMENT
    )
    assert len(filtered_suggestions) == 1
    
    # Test update_status
    reviewer_id = uuid4()
    updated_suggestion = suggestion_repository.update_status(
        suggestion1.id,
        SuggestionStatus.ACCEPTED,
        reviewer_id,
        "Looks good",
        "Approved with modifications"
    )
    assert updated_suggestion.status == SuggestionStatus.ACCEPTED
    assert updated_suggestion.reviewer_id == reviewer_id
    
    # Test get_metrics
    metrics = suggestion_repository.get_metrics()
    assert metrics["total_suggestions"] == 3
    assert metrics["acceptance_rate"] == 1/3
    assert len(metrics["suggestions_by_type"]) == 2
    
    # Test get_high_confidence_suggestions
    high_confidence = suggestion_repository.get_high_confidence_suggestions(threshold=0.9)
    assert len(high_confidence) == 3  # All suggestions have 0.95 confidence
    
    # Test get_pending_suggestions
    pending = suggestion_repository.get_pending_suggestions()
    assert len(pending) == 2 