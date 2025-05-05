import pytest
from fastapi import status
from uuid import uuid4

from app.models.enums import SuggestionStatus, SuggestionType

def test_generate_suggestions(client, sample_claim, mocker):
    # Mock the AI service
    mock_ai_service = mocker.patch("app.services.ai_service.AIService")
    mock_ai_service.return_value.analyze_claim.return_value = []
    
    response = client.post(f"/suggestions/claims/{sample_claim.id}/suggestions")
    assert response.status_code == status.HTTP_201_CREATED
    mock_ai_service.return_value.analyze_claim.assert_called_once()

def test_generate_suggestions_nonexistent_claim(client):
    response = client.post(f"/suggestions/claims/{uuid4()}/suggestions")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_claim_suggestions(client, sample_suggestion):
    response = client.get(f"/suggestions/claims/{sample_suggestion.claim_id}/suggestions")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(sample_suggestion.id)

def test_list_claim_suggestions_with_status_filter(client, sample_suggestion):
    response = client.get(
        f"/suggestions/claims/{sample_suggestion.claim_id}/suggestions",
        params={"status": SuggestionStatus.PENDING.value}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == SuggestionStatus.PENDING.value

def test_get_suggestion(client, sample_suggestion):
    response = client.get(f"/suggestions/{sample_suggestion.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(sample_suggestion.id)
    assert data["type"] == sample_suggestion.type.value
    assert data["confidence_score"] == sample_suggestion.confidence_score

def test_get_nonexistent_suggestion(client):
    response = client.get(f"/suggestions/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_review_suggestion(client, sample_suggestion):
    review_data = {
        "status": SuggestionStatus.ACCEPTED.value,
        "reviewer_id": str(uuid4()),
        "reviewer_notes": "Looks good",
        "modified_action": None
    }
    
    response = client.post(f"/suggestions/{sample_suggestion.id}/review", json=review_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == review_data["status"]
    assert data["reviewer_notes"] == review_data["reviewer_notes"]
    assert "reviewed_at" in data

def test_review_suggestion_with_modification(client, sample_suggestion):
    review_data = {
        "status": SuggestionStatus.MODIFIED.value,
        "reviewer_id": str(uuid4()),
        "reviewer_notes": "Modified action",
        "modified_action": "Updated inspection schedule"
    }
    
    response = client.post(f"/suggestions/{sample_suggestion.id}/review", json=review_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == review_data["status"]
    assert data["suggested_action"] == review_data["modified_action"]

def test_review_nonexistent_suggestion(client):
    review_data = {
        "status": SuggestionStatus.ACCEPTED.value,
        "reviewer_id": str(uuid4()),
        "reviewer_notes": "Looks good"
    }
    
    response = client.post(f"/suggestions/{uuid4()}/review", json=review_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_review_already_reviewed_suggestion(client, sample_suggestion):
    # First review
    review_data = {
        "status": SuggestionStatus.ACCEPTED.value,
        "reviewer_id": str(uuid4()),
        "reviewer_notes": "First review"
    }
    client.post(f"/suggestions/{sample_suggestion.id}/review", json=review_data)
    
    # Try to review again
    review_data["reviewer_notes"] = "Second review"
    response = client.post(f"/suggestions/{sample_suggestion.id}/review", json=review_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_suggestion_metrics(client, sample_suggestion):
    # First, review the suggestion
    review_data = {
        "status": SuggestionStatus.ACCEPTED.value,
        "reviewer_id": str(uuid4()),
        "reviewer_notes": "Looks good"
    }
    client.post(f"/suggestions/{sample_suggestion.id}/review", json=review_data)
    
    # Get metrics
    response = client.get("/suggestions/metrics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_suggestions"] == 1
    assert data["acceptance_rate"] == 1.0
    assert data["rejection_rate"] == 0.0
    assert data["modification_rate"] == 0.0
    assert len(data["suggestions_by_type"]) == 1 