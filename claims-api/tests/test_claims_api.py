import pytest
from fastapi import status
from datetime import datetime
from uuid import uuid4

from app.models.enums import ClaimStatus

def test_create_claim(client):
    claim_data = {
        "policy_number": "POL123",
        "policyholder_name": "John Doe",
        "loss_date": datetime.utcnow().isoformat(),
        "loss_description": "Water damage in kitchen",
        "loss_amount": 5000.00,
        "incident_location": "123 Main St"
    }
    
    response = client.post("/claims", json=claim_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["policy_number"] == claim_data["policy_number"]
    assert data["status"] == ClaimStatus.SUBMITTED.value
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_claim(client, sample_claim):
    response = client.get(f"/claims/{sample_claim.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(sample_claim.id)
    assert data["policy_number"] == sample_claim.policy_number

def test_get_nonexistent_claim(client):
    response = client.get(f"/claims/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_claims(client, sample_claim):
    response = client.get("/claims")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(sample_claim.id)

def test_list_claims_with_filters(client, sample_claim):
    # Test filtering by status
    response = client.get(f"/claims?status={ClaimStatus.SUBMITTED.value}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    
    # Test filtering by policyholder name
    response = client.get("/claims?policyholder_name=John")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    
    # Test with no matches
    response = client.get("/claims?status=APPROVED")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0

def test_update_claim(client, sample_claim):
    updates = {
        "status": ClaimStatus.UNDER_REVIEW.value,
        "loss_amount": 6000.00
    }
    
    response = client.patch(f"/claims/{sample_claim.id}", json=updates)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == updates["status"]
    assert data["loss_amount"] == updates["loss_amount"]
    assert data["updated_at"] != sample_claim.updated_at.isoformat()

def test_update_nonexistent_claim(client):
    updates = {"status": ClaimStatus.UNDER_REVIEW.value}
    response = client.patch(f"/claims/{uuid4()}", json=updates)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_upload_video(client, sample_claim, mocker):
    # Mock the video service
    mock_video_service = mocker.patch("app.services.video_service.VideoService")
    mock_video_service.return_value.save_video.return_value = "/tmp/test_video.mp4"
    mock_video_service.return_value.analyze_video.return_value = {"damage": "severe"}
    
    # Mock the AI service
    mock_ai_service = mocker.patch("app.services.ai_service.AIService")
    mock_ai_service.return_value.analyze_claim.return_value = []
    
    # Create a test video file
    test_video = b"fake video content"
    
    response = client.post(
        f"/claims/{sample_claim.id}/upload_video",
        files={"file": ("test.mp4", test_video, "video/mp4")}
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify the mocks were called
    mock_video_service.return_value.save_video.assert_called_once()
    mock_video_service.return_value.analyze_video.assert_called_once()
    mock_ai_service.return_value.analyze_claim.assert_called_once()

def test_upload_video_nonexistent_claim(client):
    test_video = b"fake video content"
    response = client.post(
        f"/claims/{uuid4()}/upload_video",
        files={"file": ("test.mp4", test_video, "video/mp4")}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND 