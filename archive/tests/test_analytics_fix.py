from app.database import SessionLocal
from app.models import Entry, Response, Question, User
from sqlalchemy.orm import joinedload

db = SessionLocal()
try:
    # Get test user
    user = db.query(User).filter(User.username == 'test').first()
    print(f'User: {user.username} (ID: {user.id})')
    
    # Get entries
    entries = db.query(Entry).filter(Entry.user_id == user.id).all()
    print(f'Found {len(entries)} entries')
    
    # Get responses with joinedload
    entry_ids = [e.id for e in entries]
    responses = db.query(Response).options(joinedload(Response.question)).filter(Response.entry_id.in_(entry_ids)).all()
    print(f'Found {len(responses)} responses with joinedload')
    
    # Test specific response queries
    rpe_responses = [r for r in responses if r.question and "Rate of Perceived Exertion" in r.question.question_text]
    print(f'RPE responses: {len(rpe_responses)}')
    
    rounds_responses = [r for r in responses if r.question and "Rounds Rolled" in r.question.question_text]
    print(f'Rounds responses: {len(rounds_responses)}')
    
    session_type_responses = [r for r in responses if r.question and "Session Type" in r.question.question_text]
    print(f'Session type responses: {len(session_type_responses)}')
    
    # Calculate totals
    total_rounds = sum(int(r.answer) for r in rounds_responses if r.answer.isdigit())
    print(f'Total rounds: {total_rounds}')
    
    avg_rpe = sum(int(r.answer) for r in rpe_responses) / len(rpe_responses) if rpe_responses else 0
    print(f'Average RPE: {avg_rpe}')
    
finally:
    db.close()