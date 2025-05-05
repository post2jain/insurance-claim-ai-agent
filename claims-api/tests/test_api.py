import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models.enums import ClaimStatus, SuggestionStatus, SuggestionType

client = TestClient(app)

def test_create_claim(sample_claim_data: dict):
    response = client.post("/api/claims/", json=sample_claim_data)
    assert response.status_code == 201
    data = response.json()
    assert data["policy_number"] == sample_claim_data["policy_number"]
    assert data["status"] == ClaimStatus.SUBMITTED.value
    assert "id" in data

def test_get_claim(sample_claim_data: dict):
    # Create a claim first
    create_response = client.post("/api/claims/", json=sample_claim_data)
    claim_id = create_response.json()["id"]
    
    # Get the claim
    response = client.get(f"/api/claims/{claim_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == claim_id
    assert data["policy_number"] == sample_claim_data["policy_number"]

def test_update_claim(sample_claim_data: dict):
    # Create a claim first
    create_response = client.post("/api/claims/", json=sample_claim_data)
    claim_id = create_response.json()["id"]
    
    # Update the claim
    update_data = {"policyholder_name": "Jane Doe"}
    response = client.patch(f"/api/claims/{claim_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == claim_id
    assert data["policyholder_name"] == "Jane Doe"

def test_delete_claim(sample_claim_data: dict):
    # Create a claim first
    create_response = client.post("/api/claims/", json=sample_claim_data)
    claim_id = create_response.json()["id"]
    
    # Delete the claim
    response = client.delete(f"/api/claims/{claim_id}")
    assert response.status_code == 204
    
    # Verify claim is deleted
    get_response = client.get(f"/api/claims/{claim_id}")
    assert get_response.status_code == 404

def test_upload_video(sample_claim_data: dict):
    # Create a claim first
    create_response = client.post("/api/claims/", json=sample_claim_data)
    claim_id = create_response.json()["id"]
    
    # Upload video
    video_data = b"test video data"
    response = client.post(
        f"/api/claims/{claim_id}/video",
        files={"video": ("test.mp4", video_data, "video/mp4")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "damage_detected" in data
    assert "damage_description" in data
    assert "confidence" in data

def test_get_suggestions(sample_claim_data: dict, sample_suggestion_data: dict):
    # Create a claim first
    create_response = client.post("/api/claims/", json=sample_claim_data)
    claim_id = create_response.json()["id"]
    
    # Create suggestions
    suggestion1 = {**sample_suggestion_data, "claim_id": claim_id, "type": SuggestionType.DAMAGE_ASSESSMENT}
    suggestion2 = {**sample_suggestion_data, "claim_id": claim_id, "type": SuggestionType.FRAUD_DETECTION}
    client.post("/api/suggestions/", json=suggestion1)
    client.post("/api/suggestions/", json=suggestion2)
    
    # Get suggestions
    response = client.get(f"/api/suggestions/claim/{claim_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(s["type"] == SuggestionType.DAMAGE_ASSESSMENT.value for s in data)
    assert any(s["type"] == SuggestionType.FRAUD_DETECTION.value for s in data)

def test_update_suggestion(sample_suggestion_data: dict):
    # Create a suggestion first
    create_response = client.post("/api/suggestions/", json=sample_suggestion_data)
    suggestion_id = create_response.json()["id"]
    
    # Update the suggestion
    update_data = {
        "status": SuggestionStatus.ACCEPTED.value,
        "reviewer_id": str(uuid4()),
        "review_notes": "Looks good",
        "implementation_notes": "Approved with modifications"
    }
    response = client.patch(f"/api/suggestions/{suggestion_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == suggestion_id
    assert data["status"] == SuggestionStatus.ACCEPTED.value
    assert data["review_notes"] == "Looks good"
    assert data["implementation_notes"] == "Approved with modifications"

def test_get_suggestion_metrics(sample_suggestion_data: dict):
    # Create test suggestions
    suggestion1 = {**sample_suggestion_data, "type": SuggestionType.DAMAGE_ASSESSMENT, "status": SuggestionStatus.PENDING}
    suggestion2 = {**sample_suggestion_data, "type": SuggestionType.FRAUD_DETECTION, "status": SuggestionStatus.ACCEPTED}
    client.post("/api/suggestions/", json=suggestion1)
    client.post("/api/suggestions/", json=suggestion2)
    
    # Get metrics
    response = client.get("/api/suggestions/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_suggestions"] == 2
    assert data["acceptance_rate"] == 0.5
    assert len(data["suggestions_by_type"]) == 2
    assert data["suggestions_by_type"][SuggestionType.DAMAGE_ASSESSMENT.value] == 1
    assert data["suggestions_by_type"][SuggestionType.FRAUD_DETECTION.value] == 1

def test_get_high_confidence_suggestions(sample_suggestion_data: dict):
    # Create test suggestions
    suggestion = {**sample_suggestion_data, "confidence": 0.95}
    client.post("/api/suggestions/", json=suggestion)
    
    # Get high confidence suggestions
    response = client.get("/api/suggestions/high-confidence?threshold=0.9")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["confidence"] == 0.95

def test_get_pending_suggestions(sample_suggestion_data: dict):
    # Create test suggestions
    suggestion = {**sample_suggestion_data, "status": SuggestionStatus.PENDING}
    client.post("/api/suggestions/", json=suggestion)
    
    # Get pending suggestions
    response = client.get("/api/suggestions/pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == SuggestionStatus.PENDING.value 