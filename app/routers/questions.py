from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Question
from app.schemas import Question as QuestionSchema

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/", response_model=List[QuestionSchema])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.is_active == True).order_by(Question.order_index).all()
    return questions