"""Shared test fixtures — in-memory SQLite DB + FastAPI test client."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import Question
from main import app


# In-memory SQLite for tests — StaticPool ensures all connections share the same DB
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    # Seed default questions
    db = TestingSessionLocal()
    if db.query(Question).count() == 0:
        questions = [
            Question(id=1, question_text="Session Type", question_type="select", category="general", order_index=1),
            Question(id=2, question_text="Rate of Perceived Exertion (1-9)", question_type="rating", category="physical", order_index=2),
            Question(id=3, question_text="Training", question_type="select", category="general", order_index=3),
            Question(id=4, question_text="Class Technique", question_type="text", category="technique", order_index=4),
            Question(id=5, question_text="Rounds Rolled", question_type="number", category="general", order_index=5),
            Question(id=6, question_text="Journal Notes", question_type="text", category="notes", order_index=6),
        ]
        db.add_all(questions)
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    client.post("/auth/register", json={"username": "testuser", "password": "testpass"})
    resp = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client):
    """Register a second user and return auth headers."""
    client.post("/auth/register", json={"username": "otheruser", "password": "otherpass"})
    resp = client.post("/auth/login", json={"username": "otheruser", "password": "otherpass"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
