import pytest
from unittest.mock import Mock, patch
import os
from datetime import datetime
from uuid import uuid4

from app.services.ai_service import AIService
from app.services.video_service import VideoService
from app.models.schemas import Claim, AISuggestion
from app.models.enums import SuggestionType, SuggestionStatus, ClaimStatus
from app.services.claims_service import ClaimsService
from app.services.suggestions_service import SuggestionsService

class TestAIService:
    @pytest.fixture
    def ai_service(self):
        return AIService()
    
    @pytest.fixture
    def sample_claim(self):
        return Claim(
            id=uuid4(),
            policy_number="POL123",
            policyholder_name="John Doe",
            loss_date=datetime.utcnow(),
            loss_description="Water damage in kitchen",
            loss_amount=5000.00,
            incident_location="123 Main St",
            status="SUBMITTED",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def test_analyze_claim(self, ai_service, sample_claim, mocker):
        # Mock OpenAI API call
        mock_openai = mocker.patch("openai.ChatCompletion.create")
        mock_openai.return_value = {
            "choices": [{
                "message": {
                    "content": """
                    {
                        "suggestions": [
                            {
                                "type": "INVESTIGATION",
                                "confidence_score": 0.95,
                                "explanation": "High confidence in damage assessment",
                                "suggested_action": "Schedule inspection"
                            }
                        ]
                    }
                    """
                }
            }]
        }
        
        suggestions = ai_service.analyze_claim(sample_claim)
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert isinstance(suggestion, AISuggestion)
        assert suggestion.type == SuggestionType.INVESTIGATION
        assert suggestion.confidence_score == 0.95
        assert suggestion.claim_id == sample_claim.id
        assert suggestion.status == SuggestionStatus.PENDING
    
    def test_analyze_claim_with_video(self, ai_service, sample_claim, mocker):
        # Add video analysis results to claim
        sample_claim.ml_processing_results = {
            "damage_severity": "severe",
            "affected_areas": ["kitchen", "living_room"]
        }
        
        # Mock OpenAI API call
        mock_openai = mocker.patch("openai.ChatCompletion.create")
        mock_openai.return_value = {
            "choices": [{
                "message": {
                    "content": """
                    {
                        "suggestions": [
                            {
                                "type": "INVESTIGATION",
                                "confidence_score": 0.98,
                                "explanation": "Video confirms severe damage",
                                "suggested_action": "Immediate inspection required"
                            }
                        ]
                    }
                    """
                }
            }]
        }
        
        suggestions = ai_service.analyze_claim(sample_claim)
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.confidence_score == 0.98
        assert "video" in suggestion.explanation.lower()

class TestVideoService:
    @pytest.fixture
    def video_service(self):
        return VideoService()
    
    def test_save_video(self, video_service, tmp_path):
        # Create a temporary video file
        video_content = b"fake video content"
        video_path = video_service.save_video(video_content, "test_claim")
        
        assert os.path.exists(video_path)
        with open(video_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == video_content
    
    def test_analyze_video(self, video_service, mocker):
        # Mock OpenAI Vision API call
        mock_openai = mocker.patch("openai.ChatCompletion.create")
        mock_openai.return_value = {
            "choices": [{
                "message": {
                    "content": """
                    {
                        "damage_severity": "severe",
                        "affected_areas": ["kitchen", "living_room"],
                        "estimated_repair_cost": 15000
                    }
                    """
                }
            }]
        }
        
        # Create a temporary video file
        video_path = "/tmp/test_video.mp4"
        with open(video_path, "wb") as f:
            f.write(b"fake video content")
        
        try:
            analysis = video_service.analyze_video(video_path)
            assert "damage_severity" in analysis
            assert "affected_areas" in analysis
            assert "estimated_repair_cost" in analysis
            assert analysis["damage_severity"] == "severe"
            assert len(analysis["affected_areas"]) == 2
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    def test_validate_video(self, video_service):
        # Test valid video
        valid_video = b"fake video content"
        assert video_service.validate_video(valid_video, "test.mp4")
        
        # Test invalid file type
        assert not video_service.validate_video(valid_video, "test.txt")
        
        # Test file too large
        large_video = b"x" * (101 * 1024 * 1024)  # 101MB
        assert not video_service.validate_video(large_video, "test.mp4")

def test_claims_service_create_claim(
    claims_service: ClaimsService,
    sample_claim_data: dict,
    mock_ai_service: Mock
):
    # Mock AI service response
    mock_ai_service.analyze_claim.return_value = {
        "suggestions": [
            {
                "type": SuggestionType.DAMAGE_ASSESSMENT,
                "content": "Test suggestion",
                "confidence": 0.95
            }
        ]
    }
    
    # Create claim
    claim = claims_service.create_claim(sample_claim_data)
    
    # Verify claim creation
    assert claim.id is not None
    assert claim.policy_number == sample_claim_data["policy_number"]
    assert claim.status == ClaimStatus.SUBMITTED
    
    # Verify AI service was called
    mock_ai_service.analyze_claim.assert_called_once_with(claim)

def test_claims_service_get_claim(claims_service: ClaimsService, sample_claim_data: dict):
    # Create a claim
    created_claim = claims_service.create_claim(sample_claim_data)
    
    # Get the claim
    retrieved_claim = claims_service.get_claim(created_claim.id)
    
    # Verify claim retrieval
    assert retrieved_claim is not None
    assert retrieved_claim.id == created_claim.id
    assert retrieved_claim.policy_number == sample_claim_data["policy_number"]

def test_claims_service_update_claim(claims_service: ClaimsService, sample_claim_data: dict):
    # Create a claim
    created_claim = claims_service.create_claim(sample_claim_data)
    
    # Update the claim
    update_data = {"policyholder_name": "Jane Doe"}
    updated_claim = claims_service.update_claim(created_claim.id, update_data)
    
    # Verify claim update
    assert updated_claim is not None
    assert updated_claim.id == created_claim.id
    assert updated_claim.policyholder_name == "Jane Doe"

def test_claims_service_delete_claim(claims_service: ClaimsService, sample_claim_data: dict):
    # Create a claim
    created_claim = claims_service.create_claim(sample_claim_data)
    
    # Delete the claim
    assert claims_service.delete_claim(created_claim.id) is True
    
    # Verify claim deletion
    assert claims_service.get_claim(created_claim.id) is None

def test_claims_service_process_video(
    claims_service: ClaimsService,
    sample_claim_data: dict,
    mock_video_service: Mock
):
    # Mock video service response
    mock_video_service.analyze_video.return_value = {
        "damage_detected": True,
        "damage_description": "Test damage",
        "confidence": 0.95
    }
    
    # Create a claim
    claim = claims_service.create_claim(sample_claim_data)
    
    # Process video
    video_data = b"test video data"
    result = claims_service.process_video(claim.id, video_data)
    
    # Verify video processing
    assert result is not None
    assert result["damage_detected"] is True
    assert result["damage_description"] == "Test damage"
    
    # Verify video service was called
    mock_video_service.analyze_video.assert_called_once_with(video_data)

def test_suggestions_service_get_suggestions(
    suggestions_service: SuggestionsService,
    sample_suggestion_data: dict
):
    # Create test suggestions
    claim_id = uuid4()
    suggestion1 = suggestions_service.create_suggestion({
        **sample_suggestion_data,
        "claim_id": claim_id,
        "type": SuggestionType.DAMAGE_ASSESSMENT
    })
    suggestion2 = suggestions_service.create_suggestion({
        **sample_suggestion_data,
        "claim_id": claim_id,
        "type": SuggestionType.FRAUD_DETECTION
    })
    
    # Get suggestions
    suggestions = suggestions_service.get_suggestions(claim_id)
    
    # Verify suggestions retrieval
    assert len(suggestions) == 2
    assert any(s.type == SuggestionType.DAMAGE_ASSESSMENT for s in suggestions)
    assert any(s.type == SuggestionType.FRAUD_DETECTION for s in suggestions)

def test_suggestions_service_update_suggestion(
    suggestions_service: SuggestionsService,
    sample_suggestion_data: dict
):
    # Create a suggestion
    suggestion = suggestions_service.create_suggestion(sample_suggestion_data)
    
    # Update the suggestion
    reviewer_id = uuid4()
    update_data = {
        "status": SuggestionStatus.ACCEPTED,
        "reviewer_id": reviewer_id,
        "review_notes": "Looks good",
        "implementation_notes": "Approved with modifications"
    }
    updated_suggestion = suggestions_service.update_suggestion(suggestion.id, update_data)
    
    # Verify suggestion update
    assert updated_suggestion is not None
    assert updated_suggestion.id == suggestion.id
    assert updated_suggestion.status == SuggestionStatus.ACCEPTED
    assert updated_suggestion.reviewer_id == reviewer_id
    assert updated_suggestion.review_notes == "Looks good"
    assert updated_suggestion.implementation_notes == "Approved with modifications"

def test_suggestions_service_get_metrics(
    suggestions_service: SuggestionsService,
    sample_suggestion_data: dict
):
    # Create test suggestions
    suggestion1 = suggestions_service.create_suggestion({
        **sample_suggestion_data,
        "type": SuggestionType.DAMAGE_ASSESSMENT,
        "status": SuggestionStatus.PENDING
    })
    suggestion2 = suggestions_service.create_suggestion({
        **sample_suggestion_data,
        "type": SuggestionType.FRAUD_DETECTION,
        "status": SuggestionStatus.ACCEPTED
    })
    
    # Get metrics
    metrics = suggestions_service.get_metrics()
    
    # Verify metrics
    assert metrics["total_suggestions"] == 2
    assert metrics["acceptance_rate"] == 0.5
    assert len(metrics["suggestions_by_type"]) == 2
    assert metrics["suggestions_by_type"][SuggestionType.DAMAGE_ASSESSMENT] == 1
    assert metrics["suggestions_by_type"][SuggestionType.FRAUD_DETECTION] == 1 