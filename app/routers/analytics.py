from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.database import get_db
from app.models import Entry, Response, Question, User
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_dashboard_stats(
    period: Optional[str] = Query("30d", description="Time period: 7d, 30d, this_month, 6m, 1y, all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    # Calculate date filter
    now = datetime.now()
    if period == "7d":
        start_date = now - timedelta(days=7)
    elif period == "30d":
        start_date = now - timedelta(days=30)
    elif period == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "6m":
        start_date = now - timedelta(days=180)
    elif period == "1y":
        start_date = now - timedelta(days=365)
    else:  # "all"
        start_date = None
    
    # Get filtered entries
    if start_date:
        entries = db.query(Entry).filter(
            Entry.user_id == current_user.id,
            Entry.date >= start_date
        ).all()
    else:
        entries = db.query(Entry).filter(Entry.user_id == current_user.id).all()
    
    if not entries:
        return {
            "total_sessions": 0,
            "this_month": 0,
            "avg_rpe": 0,
            "total_rounds": 0,
            "session_types": {},
            "training_types": {},
            "rpe_distribution": {},
            "monthly_trend": []
        }
    
    # Basic stats
    total_sessions = len(entries)
    
    # This month sessions
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month = len([e for e in entries if e.date.month == current_month and e.date.year == current_year])
    
    # Get all responses for analysis
    entry_ids = [e.id for e in entries]
    responses = db.query(Response).filter(Response.entry_id.in_(entry_ids)).all()
    
    # RPE analysis
    rpe_responses = [r for r in responses if "Rate of Perceived Exertion" in r.question.question_text]
    avg_rpe = sum(int(r.answer) for r in rpe_responses) / len(rpe_responses) if rpe_responses else 0
    
    # RPE distribution
    rpe_distribution = {}
    for r in rpe_responses:
        rpe = int(r.answer)
        rpe_distribution[rpe] = rpe_distribution.get(rpe, 0) + 1
    
    # Total rounds
    rounds_responses = [r for r in responses if "Rounds Rolled" in r.question.question_text]
    total_rounds = sum(int(r.answer) for r in rounds_responses if r.answer.isdigit())
    
    # Session types
    session_type_responses = [r for r in responses if "Session Type" in r.question.question_text]
    session_types = {}
    for r in session_type_responses:
        session_types[r.answer] = session_types.get(r.answer, 0) + 1
    
    # Training types
    training_type_responses = [r for r in responses if r.question.question_text == "Training"]
    training_types = {}
    for r in training_type_responses:
        training_types[r.answer] = training_types.get(r.answer, 0) + 1
    
    # Monthly trend (last 6 months)
    monthly_trend = []
    for i in range(6):
        target_date = datetime.now() - timedelta(days=30*i)
        month_entries = [e for e in entries if e.date.month == target_date.month and e.date.year == target_date.year]
        monthly_trend.append({
            "month": target_date.strftime("%b %Y"),
            "sessions": len(month_entries)
        })
    
    # RPE trend over time (last 10 sessions)
    rpe_trend = []
    entries_sorted = sorted(entries, key=lambda x: x.date)
    for entry in entries_sorted[-10:]:
        entry_rpe = next((int(r.answer) for r in responses if r.entry_id == entry.id and "Rate of Perceived Exertion" in r.question.question_text), None)
        if entry_rpe:
            rpe_trend.append({
                "date": entry.date.strftime("%d/%m"),
                "rpe": entry_rpe
            })
    
    # Weekly training volume (last 4 weeks)
    weekly_volume = []
    for i in range(4):
        week_start = now - timedelta(days=7*(i+1))
        week_end = week_start + timedelta(days=7)
        week_entries = [e for e in entries if week_start <= e.date <= week_end]
        week_rounds = sum(int(r.answer) for r in responses if r.entry_id in [e.id for e in week_entries] and "Rounds Rolled" in r.question.question_text and r.answer.isdigit())
        
        # Format date range
        start_str = week_start.strftime("%d/%m")
        end_str = (week_end - timedelta(days=1)).strftime("%d/%m")
        date_range = f"{start_str} - {end_str}"
        
        weekly_volume.append({
            "week": f"Week {4-i}",
            "date_range": date_range,
            "rounds": week_rounds,
            "sessions": len(week_entries)
        })
    
    # Rounds by session type
    rounds_by_session_type = {"Gi": 0, "No Gi": 0, "Both": 0}
    for entry in entries:
        entry_session_type = next((r.answer for r in responses if r.entry_id == entry.id and "Session Type" in r.question.question_text), None)
        entry_rounds = next((int(r.answer) for r in responses if r.entry_id == entry.id and "Rounds Rolled" in r.question.question_text and r.answer.isdigit()), 0)
        if entry_session_type and entry_rounds:
            rounds_by_session_type[entry_session_type] += entry_rounds
    
    # RPE vs Rounds correlation data
    rpe_rounds_correlation = []
    for entry in entries:
        entry_rpe = next((int(r.answer) for r in responses if r.entry_id == entry.id and "Rate of Perceived Exertion" in r.question.question_text), None)
        entry_rounds = next((int(r.answer) for r in responses if r.entry_id == entry.id and "Rounds Rolled" in r.question.question_text and r.answer.isdigit()), None)
        if entry_rpe and entry_rounds:
            rpe_rounds_correlation.append({
                "rpe": entry_rpe,
                "rounds": entry_rounds
            })
    
    return {
        "total_sessions": total_sessions,
        "this_month": this_month,
        "avg_rpe": round(avg_rpe, 1),
        "total_rounds": total_rounds,
        "session_types": session_types,
        "training_types": training_types,
        "rpe_distribution": rpe_distribution,
        "monthly_trend": list(reversed(monthly_trend)),
        "rpe_trend": rpe_trend,
        "weekly_volume": weekly_volume,
        "rounds_by_session_type": rounds_by_session_type,
        "rpe_rounds_correlation": rpe_rounds_correlation
    }