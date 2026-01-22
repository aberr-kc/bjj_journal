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
    try:
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
        
        # Get all responses for analysis - with error handling
        entry_ids = [e.id for e in entries]
        try:
            responses = db.query(Response).filter(Response.entry_id.in_(entry_ids)).all()
        except Exception as e:
            print(f"Error loading responses: {e}")
            responses = []
    
    # RPE analysis
    rpe_responses = [r for r in responses if r.question and "Rate of Perceived Exertion" in r.question.question_text]
    avg_rpe = sum(int(r.answer) for r in rpe_responses) / len(rpe_responses) if rpe_responses else 0
    
    # RPE distribution
    rpe_distribution = {}
    for r in rpe_responses:
        rpe = int(r.answer)
        rpe_distribution[rpe] = rpe_distribution.get(rpe, 0) + 1
    
    # Total rounds
    rounds_responses = [r for r in responses if r.question and "Rounds Rolled" in r.question.question_text]
    total_rounds = sum(int(r.answer) for r in rounds_responses if r.answer.isdigit())
    
    # Session types
    session_type_responses = [r for r in responses if r.question and "Session Type" in r.question.question_text]
    session_types = {}
    for r in session_type_responses:
        session_types[r.answer] = session_types.get(r.answer, 0) + 1
    
    # Training types
    training_type_responses = [r for r in responses if r.question and r.question.question_text == "Training"]
    training_types = {}
    for r in training_type_responses:
        training_types[r.answer] = training_types.get(r.answer, 0) + 1
    
    # Submissions analysis
    technique_responses = [r for r in responses if r.question and "Class Technique" in r.question.question_text]
    submissions = {}
    positions = {}
    for r in technique_responses:
        # Extract submission from "Position - Submission" format
        if " - " in r.answer:
            parts = r.answer.split(" - ")
            if len(parts) >= 2:
                position = parts[0].strip()
                technique_type = parts[1].strip()
                
                # Count positions/areas
                positions[position] = positions.get(position, 0) + 1
                
                # Only count if it's a submission (not sweeps, escapes, etc.)
                submission_keywords = [
                    'Choke', 'Triangle', 'Armbar', 'Kimura', 'Omoplata', 'Americana', 
                    'Heel Hook', 'Toe Hold', 'Kneebar', 'Lock', 'Slicer', 'Crusher',
                    'Guillotine', 'D\'Arce', 'Anaconda', 'Bow and Arrow', 'Cross Collar',
                    'Baseball', 'Ezekiel', 'Paper Cutter', 'Loop', 'Peruvian', 'Japanese',
                    'Gogoplata', 'Von Flue', 'Twister', 'Crank', 'Wrist'
                ]
                if any(keyword.lower() in technique_type.lower() for keyword in submission_keywords):
                    submissions[technique_type] = submissions.get(technique_type, 0) + 1
    
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
        entry_rpe = next((int(r.answer) for r in responses if r.entry_id == entry.id and r.question and "Rate of Perceived Exertion" in r.question.question_text), None)
        if entry_rpe:
            rpe_trend.append({
                "date": entry.date.strftime("%d/%m"),
                "rpe": entry_rpe
            })
    
    # Weekly training volume based on period
    weekly_volume = []
    if period == "7d":
        # Show daily for last 7 days
        for i in range(7):
            day_start = now - timedelta(days=i+1)
            day_end = day_start + timedelta(days=1)
            day_entries = [e for e in entries if day_start <= e.date < day_end]
            day_rounds = sum(int(r.answer) for r in responses if r.entry_id in [e.id for e in day_entries] and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit())
            
            weekly_volume.append({
                "period": day_start.strftime("%d/%m"),
                "date_range": day_start.strftime("%d/%m"),
                "rounds": day_rounds,
                "sessions": len(day_entries)
            })
    elif period == "30d":
        # Show 4 weeks for last 30 days
        for i in range(4):
            week_start = now - timedelta(days=7*(i+1))
            week_end = week_start + timedelta(days=7)
            week_entries = [e for e in entries if week_start <= e.date <= week_end]
            week_rounds = sum(int(r.answer) for r in responses if r.entry_id in [e.id for e in week_entries] and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit())
            
            start_str = week_start.strftime("%d/%m")
            end_str = (week_end - timedelta(days=1)).strftime("%d/%m")
            
            weekly_volume.append({
                "period": f"Week {4-i}",
                "date_range": f"{start_str} - {end_str}",
                "rounds": week_rounds,
                "sessions": len(week_entries)
            })
    elif period == "6m":
        # Show 6 months
        for i in range(6):
            month_start = (now - timedelta(days=30*i)).replace(day=1)
            if i == 0:
                month_end = now
            else:
                month_end = month_start.replace(day=28) + timedelta(days=4)
                month_end = month_end - timedelta(days=month_end.day)
            
            month_entries = [e for e in entries if month_start <= e.date <= month_end]
            month_rounds = sum(int(r.answer) for r in responses if r.entry_id in [e.id for e in month_entries] and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit())
            
            weekly_volume.append({
                "period": month_start.strftime("%b %Y"),
                "date_range": month_start.strftime("%b %Y"),
                "rounds": month_rounds,
                "sessions": len(month_entries)
            })
    elif period == "1y":
        # Show 12 months
        for i in range(12):
            month_start = (now - timedelta(days=30*i)).replace(day=1)
            if i == 0:
                month_end = now
            else:
                month_end = month_start.replace(day=28) + timedelta(days=4)
                month_end = month_end - timedelta(days=month_end.day)
            
            month_entries = [e for e in entries if month_start <= e.date <= month_end]
            month_rounds = sum(int(r.answer) for r in responses if r.entry_id in [e.id for e in month_entries] and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit())
            
            weekly_volume.append({
                "period": month_start.strftime("%b %Y"),
                "date_range": month_start.strftime("%b %Y"),
                "rounds": month_rounds,
                "sessions": len(month_entries)
            })
    else:
        # Show last 4 weeks for other periods
        for i in range(4):
            week_start = now - timedelta(days=7*(i+1))
            week_end = week_start + timedelta(days=7)
            week_entries = [e for e in entries if week_start <= e.date <= week_end]
            week_rounds = sum(int(r.answer) for r in responses if r.entry_id in [e.id for e in week_entries] and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit())
            
            start_str = week_start.strftime("%d/%m")
            end_str = (week_end - timedelta(days=1)).strftime("%d/%m")
            
            weekly_volume.append({
                "period": f"Week {4-i}",
                "date_range": f"{start_str} - {end_str}",
                "rounds": week_rounds,
                "sessions": len(week_entries)
            })
    
    weekly_volume.reverse()  # Show oldest to newest
    
    # Rounds by session type
    rounds_by_session_type = {"Gi": 0, "No Gi": 0, "Both": 0}
    for entry in entries:
        entry_session_type = next((r.answer for r in responses if r.entry_id == entry.id and r.question and "Session Type" in r.question.question_text), None)
        entry_rounds = next((int(r.answer) for r in responses if r.entry_id == entry.id and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit()), 0)
        if entry_session_type and entry_rounds:
            rounds_by_session_type[entry_session_type] += entry_rounds
    
    # RPE vs Rounds correlation data
    rpe_rounds_correlation = []
    for entry in entries:
        entry_rpe = next((int(r.answer) for r in responses if r.entry_id == entry.id and r.question and "Rate of Perceived Exertion" in r.question.question_text), None)
        entry_rounds = next((int(r.answer) for r in responses if r.entry_id == entry.id and r.question and "Rounds Rolled" in r.question.question_text and r.answer.isdigit()), None)
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
            "submissions": submissions,
            "positions": positions,
            "rpe_distribution": rpe_distribution,
            "monthly_trend": list(reversed(monthly_trend)),
            "rpe_trend": rpe_trend,
            "weekly_volume": weekly_volume,
            "rounds_by_session_type": rounds_by_session_type,
            "rpe_rounds_correlation": rpe_rounds_correlation
        }
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        # Return minimal safe data
        return {
            "total_sessions": 0,
            "this_month": 0,
            "avg_rpe": 0,
            "total_rounds": 0,
            "session_types": {},
            "training_types": {},
            "submissions": {},
            "positions": {},
            "rpe_distribution": {},
            "monthly_trend": [],
            "rpe_trend": [],
            "weekly_volume": [],
            "rounds_by_session_type": {"Gi": 0, "No Gi": 0, "Both": 0},
            "rpe_rounds_correlation": []
        }