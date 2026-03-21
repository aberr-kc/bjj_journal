from app.database import SessionLocal
from app.models import Question

db = SessionLocal()
try:
    # Delete all existing questions
    db.query(Question).delete()
    
    # Create new BJJ questions
    new_questions = [
        {"question_text": "Session Type", "question_type": "select", "category": "general", "order_index": 1},
        {"question_text": "Rate of Perceived Exertion (1-9)", "question_type": "rating", "category": "physical", "order_index": 2},
        {"question_text": "Training", "question_type": "select", "category": "general", "order_index": 3},
        {"question_text": "Class Technique", "question_type": "text", "category": "technique", "order_index": 4},
        {"question_text": "Journal Notes", "question_type": "text", "category": "notes", "order_index": 5},
        {"question_text": "Summarise this session with a few words", "question_type": "text", "category": "summary", "order_index": 6}
    ]
    
    for q_data in new_questions:
        question = Question(**q_data)
        db.add(question)
    
    db.commit()
    print("Questions updated successfully!")
    
finally:
    db.close()