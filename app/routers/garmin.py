from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models import Entry, Response, User
from app.dependencies import get_current_user

router = APIRouter(prefix="/garmin", tags=["garmin"])

class GarminActivityData(BaseModel):
    activity_name: str
    duration_minutes: int
    calories: int
    avg_heart_rate: int
    max_heart_rate: int
    timestamp: datetime
    activity_id: Optional[str] = None

class WidgetData(BaseModel):
    last_session: Optional[Dict[str, Any]] = None
    weekly_sessions: int = 0
    current_streak: int = 0
    avg_rpe: float = 0.0
    pending_count: int = 0

@router.post("/activity")
def receive_garmin_activity(
    activity: GarminActivityData,
    db: Session = Depends(get_db)
):
    """Receive activity data from Garmin and create pending journal entry"""
    
    # For now, create entry for user ID 1 (will enhance with proper user mapping later)
    user = db.query(User).first()
    if not user:
        # Create a default user for testing
        from app.dependencies import get_password_hash
        user = User(
            username="garmin_user",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create pending entry with Garmin data
    entry = Entry(
        user_id=user.id,
        date=activity.timestamp,
        session_type="training",  # Default, will be updated when journal completed
        garmin_activity_id=activity.activity_id,
        duration_minutes=activity.duration_minutes,
        calories_burned=activity.calories,
        avg_heart_rate=activity.avg_heart_rate,
        max_heart_rate=activity.max_heart_rate,
        is_pending=True,
        garmin_synced_at=datetime.utcnow()
    )
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return {
        "message": "Activity received",
        "entry_id": entry.id,
        "status": "pending_completion"
    }

@router.get("/widget-data", response_model=WidgetData)
def get_widget_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary data for Garmin watch widget"""
    
    # Get user's entries
    entries = db.query(Entry).filter(Entry.user_id == current_user.id).all()
    
    if not entries:
        return WidgetData()
    
    # Get last completed session
    completed_entries = [e for e in entries if not e.is_pending]
    last_session = None
    
    if completed_entries:
        latest_entry = max(completed_entries, key=lambda x: x.date)
        
        # Get responses for the latest entry
        responses = {}
        for response in latest_entry.responses:
            responses[response.question.question_text] = response.answer
        
        last_session = {
            "date": latest_entry.date.strftime("%d/%m/%y"),
            "rpe": responses.get("Rate of Perceived Exertion (1-9)", "N/A"),
            "session_type": responses.get("Session Type", "Training"),
            "training_type": responses.get("Training", ""),
            "rounds": responses.get("Rounds Rolled", "0"),
            "summary": responses.get("Summarise this session with a few words", "")
        }
    
    # Calculate stats
    from datetime import datetime, timedelta
    now = datetime.now()
    week_start = now - timedelta(days=7)
    
    weekly_sessions = len([e for e in completed_entries if e.date >= week_start])
    pending_count = len([e for e in entries if e.is_pending])
    
    # Calculate average RPE
    rpe_responses = []
    for entry in completed_entries:
        for response in entry.responses:
            if "Rate of Perceived Exertion" in response.question.question_text:
                try:
                    rpe_responses.append(int(response.answer))
                except ValueError:
                    pass
    
    avg_rpe = sum(rpe_responses) / len(rpe_responses) if rpe_responses else 0.0
    
    # Simple streak calculation (consecutive days with training)
    current_streak = 0
    sorted_entries = sorted(completed_entries, key=lambda x: x.date, reverse=True)
    current_date = now.date()
    
    for entry in sorted_entries:
        entry_date = entry.date.date()
        if entry_date == current_date or entry_date == current_date - timedelta(days=1):
            current_streak += 1
            current_date = entry_date - timedelta(days=1)
        else:
            break
    
    return WidgetData(
        last_session=last_session,
        weekly_sessions=weekly_sessions,
        current_streak=current_streak,
        avg_rpe=round(avg_rpe, 1),
        pending_count=pending_count
    )