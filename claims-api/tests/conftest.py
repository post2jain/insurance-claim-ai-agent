import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from datetime import datetime
from unittest.mock import Mock

from app.main import app
from app.database import Base, get_db
from app.models.schemas import Claim, AISuggestion
from app.models.enums import ClaimStatus, SuggestionStatus, SuggestionType
from app.repositories.claim_repository import ClaimRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.claims_service import ClaimsService
from app.services.suggestions_service import SuggestionsService
from app.services.ai_service import AIService
from app.services.video_service import VideoService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def claim_repository(db_session):
    return ClaimRepository(db_session)

@pytest.fixture(scope="function")
def suggestion_repository(db_session):
    return SuggestionRepository(db_session)

@pytest.fixture(scope="function")
def mock_ai_service():
    return Mock(spec=AIService)

@pytest.fixture(scope="function")
def mock_video_service():
    return Mock(spec=VideoService)

@pytest.fixture(scope="function")
def claims_service(claim_repository, mock_ai_service, mock_video_service):
    return ClaimsService(claim_repository, mock_ai_service, mock_video_service)

@pytest.fixture(scope="function")
def suggestions_service(suggestion_repository, mock_ai_service):
    return SuggestionsService(suggestion_repository, mock_ai_service)

@pytest.fixture
def sample_claim(db_session):
    claim = Claim(
        id=uuid4(),
        policy_number="POL123",
        policyholder_name="John Doe",
        loss_date=datetime.utcnow(),
        loss_description="Water damage in kitchen",
        loss_amount=5000.00,
        incident_location="123 Main St",
        status=ClaimStatus.SUBMITTED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    return claim

@pytest.fixture
def sample_suggestion(db_session, sample_claim):
    suggestion = AISuggestion(
        id=uuid4(),
        claim_id=sample_claim.id,
        type=SuggestionType.INVESTIGATION,
        confidence_score=0.95,
        explanation="High confidence in damage assessment",
        suggested_action="Schedule inspection",
        status=SuggestionStatus.PENDING,
        created_at=datetime.utcnow()
    )
    db_session.add(suggestion)
    db_session.commit()
    db_session.refresh(suggestion)
    return suggestion

@pytest.fixture
def sample_claim_data():
    return {
        "policy_number": "POL-123",
        "policyholder_name": "John Doe",
        "incident_date": datetime.now().isoformat(),
        "incident_description": "Test incident",
        "damage_description": "Test damage",
        "status": ClaimStatus.SUBMITTED.value
    }

@pytest.fixture
def sample_suggestion_data():
    return {
        "claim_id": str(uuid4()),
        "type": SuggestionType.DAMAGE_ASSESSMENT.value,
        "content": "Test suggestion",
        "confidence": 0.95,
        "status": SuggestionStatus.PENDING.value,
        "created_at": datetime.now().isoformat()
    } 