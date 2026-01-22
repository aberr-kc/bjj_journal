from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.database import engine, SessionLocal
from app.models import Base, Question
from app.routers import auth, entries, questions, analytics, profile
import os

# Create database tables (only for local development)
if not os.getenv("DATABASE_URL"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="BJJ Training Journal", version="1.0.1")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local HTML file
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(questions.router)
app.include_router(analytics.router)
app.include_router(profile.router)

@app.get("/")
def serve_frontend():
    return FileResponse("frontend.html")

@app.get("/mobile")
def serve_mobile():
    return FileResponse("mobile.html")

@app.on_event("startup")
def create_default_questions():
    # Only seed data in local development
    if os.getenv("DATABASE_URL"):
        return  # Skip seeding in production
        
    db = SessionLocal()
    try:
        # Check if questions already exist
        if db.query(Question).first():
            return
        
        # Create new BJJ questions
        default_questions = [
            {"question_text": "Session Type", "question_type": "select", "category": "general", "order_index": 1},
            {"question_text": "Rate of Perceived Exertion (1-9)", "question_type": "rating", "category": "physical", "order_index": 2},
            {"question_text": "Training", "question_type": "select", "category": "general", "order_index": 3},
            {"question_text": "Class Technique", "question_type": "text", "category": "technique", "order_index": 4},
            {"question_text": "Rounds Rolled", "question_type": "number", "category": "general", "order_index": 5},
            {"question_text": "Journal Notes", "question_type": "text", "category": "notes", "order_index": 6},
            {"question_text": "Summarise this session with a few words", "question_type": "text", "category": "summary", "order_index": 7}
        ]
        
        for q_data in default_questions:
            question = Question(**q_data)
            db.add(question)
        
        db.commit()
    finally:
        db.close()