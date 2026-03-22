from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, Integer
from datetime import date, datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models import User, UserGoal, WeeklyProgress, StreakHistory, Entry, TechniqueGoal, Response, Question
from app.schemas import UserGoalCreate, UserGoal as UserGoalSchema, WeeklyProgressCreate, WeeklyProgress as WeeklyProgressSchema, StreakHistory as StreakHistorySchema, CurrentStreakResponse, TechniqueGoalCreate, TechniqueGoalResponse, TechniqueGoalComplete
from app.dependencies import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])

def get_week_start(target_date: date) -> date:
    """Get the Monday of the week containing the target date"""
    days_since_monday = target_date.weekday()
    return target_date - timedelta(days=days_since_monday)

def calculate_sessions_in_week(db: Session, user_id: int, week_start: date) -> int:
    """Count training sessions in a specific week"""
    week_end = week_start + timedelta(days=6)
    return db.query(Entry).filter(
        and_(
            Entry.user_id == user_id,
            func.date(Entry.date) >= week_start,
            func.date(Entry.date) <= week_end
        )
    ).count()

def update_weekly_progress(db: Session, user_id: int, week_start: date):
    """Update or create weekly progress record"""
    # Get current goal
    current_goal = db.query(UserGoal).filter(
        and_(UserGoal.user_id == user_id, UserGoal.is_active == True)
    ).first()
    
    if not current_goal:
        return
    
    # Get or create weekly progress
    progress = db.query(WeeklyProgress).filter(
        and_(
            WeeklyProgress.user_id == user_id,
            WeeklyProgress.week_start_date == week_start
        )
    ).first()
    
    if not progress:
        progress = WeeklyProgress(
            user_id=user_id,
            week_start_date=week_start,
            sessions_completed=0,
            goal_met=False,
            is_paused=False,
            streak_count=0
        )
        db.add(progress)
    
    # Update sessions completed
    progress.sessions_completed = calculate_sessions_in_week(db, user_id, week_start)
    progress.goal_met = progress.sessions_completed >= current_goal.weekly_sessions_target and not progress.is_paused
    
    # Calculate streak
    calculate_streak(db, user_id, week_start)
    
    db.commit()

def calculate_streak(db: Session, user_id: int, current_week: date):
    """Calculate and update streak information"""
    # Get all weekly progress ordered by week
    all_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == user_id
    ).order_by(WeeklyProgress.week_start_date).all()
    
    if not all_progress:
        return
    
    # Calculate current streak
    current_streak = 0
    max_streak = 0
    temp_streak = 0
    
    for progress in all_progress:
        if progress.goal_met or progress.is_paused:
            temp_streak += 1
            if progress.week_start_date <= current_week:
                current_streak = temp_streak
        else:
            temp_streak = 0
        
        max_streak = max(max_streak, temp_streak)
    
    # Update streak counts in progress records
    for i, progress in enumerate(all_progress):
        if progress.week_start_date <= current_week:
            if progress.goal_met or progress.is_paused:
                # Count backwards to find streak start
                streak_count = 1
                for j in range(i - 1, -1, -1):
                    if all_progress[j].goal_met or all_progress[j].is_paused:
                        streak_count += 1
                    else:
                        break
                progress.streak_count = streak_count
            else:
                progress.streak_count = 0
    
    # Update streak history
    update_streak_history(db, user_id, current_streak, max_streak)
    
    db.commit()

def update_streak_history(db: Session, user_id: int, current_streak: int, max_streak: int):
    """Update streak history records"""
    # Mark all previous streaks as not current
    db.query(StreakHistory).filter(
        and_(StreakHistory.user_id == user_id, StreakHistory.is_current == True)
    ).update({StreakHistory.is_current: False})
    
    # Create or update current streak record
    if current_streak > 0:
        current_streak_record = StreakHistory(
            user_id=user_id,
            streak_length=current_streak,
            start_date=date.today() - timedelta(weeks=current_streak-1),
            is_current=True
        )
        db.add(current_streak_record)

@router.post("/", response_model=UserGoalSchema)
def create_or_update_goal(
    goal: UserGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user's weekly training goal"""
    # Deactivate existing goals
    db.query(UserGoal).filter(
        and_(UserGoal.user_id == current_user.id, UserGoal.is_active == True)
    ).update({UserGoal.is_active: False})
    
    # Create new goal
    new_goal = UserGoal(
        user_id=current_user.id,
        weekly_sessions_target=goal.weekly_sessions_target,
        weekly_rounds_target=goal.weekly_rounds_target,
        start_date=goal.start_date,
        is_active=True
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    # Update progress for current week
    current_week = get_week_start(date.today())
    update_weekly_progress(db, current_user.id, current_week)
    
    return new_goal

@router.put("/", response_model=UserGoalSchema)
def update_goal(
    goal_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's weekly training goal"""
    # Deactivate existing goals
    db.query(UserGoal).filter(
        and_(UserGoal.user_id == current_user.id, UserGoal.is_active == True)
    ).update({UserGoal.is_active: False})
    
    # Create new goal
    new_goal = UserGoal(
        user_id=current_user.id,
        weekly_sessions_target=goal_data.get('weekly_sessions_target'),
        weekly_rounds_target=goal_data.get('weekly_rounds_target'),
        start_date=date.today(),
        is_active=True
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    # Update progress for current week
    current_week = get_week_start(date.today())
    update_weekly_progress(db, current_user.id, current_week)
    
    return new_goal

@router.get("/current", response_model=Optional[UserGoalSchema])
def get_current_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current active goal"""
    return db.query(UserGoal).filter(
        and_(UserGoal.user_id == current_user.id, UserGoal.is_active == True)
    ).first()

@router.get("/history", response_model=List[UserGoalSchema])
def get_goal_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's goal history"""
    return db.query(UserGoal).filter(
        UserGoal.user_id == current_user.id
    ).order_by(desc(UserGoal.created_at)).all()

@router.get("/progress/current-week", response_model=Optional[WeeklyProgressSchema])
def get_current_week_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current week's progress"""
    current_week = get_week_start(date.today())
    update_weekly_progress(db, current_user.id, current_week)
    
    return db.query(WeeklyProgress).filter(
        and_(
            WeeklyProgress.user_id == current_user.id,
            WeeklyProgress.week_start_date == current_week
        )
    ).first()

@router.get("/progress/weekly/{week_date}", response_model=Optional[WeeklyProgressSchema])
def get_weekly_progress(
    week_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for a specific week"""
    week_start = get_week_start(week_date)
    update_weekly_progress(db, current_user.id, week_start)
    
    return db.query(WeeklyProgress).filter(
        and_(
            WeeklyProgress.user_id == current_user.id,
            WeeklyProgress.week_start_date == week_start
        )
    ).first()

@router.post("/progress/pause-week")
def pause_week(
    week_data: WeeklyProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a week as paused (injury/deload)"""
    week_start = get_week_start(week_data.week_start_date)
    
    # Get or create weekly progress
    progress = db.query(WeeklyProgress).filter(
        and_(
            WeeklyProgress.user_id == current_user.id,
            WeeklyProgress.week_start_date == week_start
        )
    ).first()
    
    if not progress:
        progress = WeeklyProgress(
            user_id=current_user.id,
            week_start_date=week_start,
            sessions_completed=0,
            goal_met=False,
            is_paused=True,
            streak_count=0
        )
        db.add(progress)
    else:
        progress.is_paused = week_data.is_paused
        progress.goal_met = progress.is_paused or (progress.sessions_completed >= 
                                                  db.query(UserGoal).filter(
                                                      and_(UserGoal.user_id == current_user.id, 
                                                           UserGoal.is_active == True)
                                                  ).first().weekly_sessions_target)
    
    db.commit()
    
    # Recalculate streaks
    calculate_streak(db, current_user.id, week_start)
    
    return {"message": "Week pause status updated"}

@router.get("/streaks/current", response_model=CurrentStreakResponse)
def get_current_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current streak information"""
    current_week = get_week_start(date.today())
    update_weekly_progress(db, current_user.id, current_week)
    
    # Get current week progress
    current_progress = db.query(WeeklyProgress).filter(
        and_(
            WeeklyProgress.user_id == current_user.id,
            WeeklyProgress.week_start_date == current_week
        )
    ).first()
    
    # Get current goal
    current_goal = db.query(UserGoal).filter(
        and_(UserGoal.user_id == current_user.id, UserGoal.is_active == True)
    ).first()
    
    # Get longest streak
    longest_streak = db.query(func.max(StreakHistory.streak_length)).filter(
        StreakHistory.user_id == current_user.id
    ).scalar() or 0
    
    # Calculate rounds for current week
    from app.models import Response, Question
    week_end = current_week + timedelta(days=6)
    rounds_query = db.query(func.sum(func.cast(Response.answer, Integer))).join(
        Entry, Response.entry_id == Entry.id
    ).join(
        Question, Response.question_id == Question.id
    ).filter(
        and_(
            Entry.user_id == current_user.id,
            func.date(Entry.date) >= current_week,
            func.date(Entry.date) <= week_end,
            Question.question_text == 'Rounds Rolled'
        )
    ).scalar()
    
    current_week_rounds = rounds_query or 0
    
    current_streak = current_progress.streak_count if current_progress else 0
    current_week_progress = current_progress.sessions_completed if current_progress else 0
    current_week_goal = current_goal.weekly_sessions_target if current_goal else 0
    current_week_rounds_goal = current_goal.weekly_rounds_target if current_goal else 0
    weeks_until_goal = max(0, current_week_goal - current_week_progress) if current_goal else 0
    
    return CurrentStreakResponse(
        current_streak=current_streak,
        longest_streak=longest_streak,
        current_week_progress=current_week_progress,
        current_week_goal=current_week_goal,
        weeks_until_goal=weeks_until_goal,
        current_week_rounds=current_week_rounds,
        current_week_rounds_goal=current_week_rounds_goal
    )

@router.get("/streaks/longest", response_model=List[StreakHistorySchema])
def get_longest_streaks(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get longest streaks achieved"""
    return db.query(StreakHistory).filter(
        StreakHistory.user_id == current_user.id
    ).order_by(desc(StreakHistory.streak_length)).limit(limit).all()


# --- Technique Goals ---

@router.get("/techniques", response_model=List[TechniqueGoalResponse])
def get_technique_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active technique goals"""
    return db.query(TechniqueGoal).filter(
        and_(TechniqueGoal.user_id == current_user.id, TechniqueGoal.is_active == True)
    ).order_by(TechniqueGoal.created_at).all()

@router.post("/techniques", response_model=TechniqueGoalResponse)
def create_technique_goal(
    goal: TechniqueGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new technique goal"""
    new_goal = TechniqueGoal(
        user_id=current_user.id,
        position=goal.position,
        notes=goal.notes,
        timeline_weeks=goal.timeline_weeks,
        is_active=True
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.delete("/techniques/{goal_id}")
def delete_technique_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a technique goal (soft delete)"""
    goal = db.query(TechniqueGoal).filter(
        and_(TechniqueGoal.id == goal_id, TechniqueGoal.user_id == current_user.id)
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Technique goal not found")
    goal.is_active = False
    goal.status = "archived"
    goal.completed_at = datetime.utcnow()
    db.commit()
    return {"message": "Technique goal archived"}


@router.get("/techniques/progress")
def get_technique_goals_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress data for each active technique goal."""
    goals = db.query(TechniqueGoal).filter(
        and_(TechniqueGoal.user_id == current_user.id, TechniqueGoal.is_active == True)
    ).order_by(TechniqueGoal.created_at).all()

    if not goals:
        return []

    results = []
    for goal in goals:
        created_at = goal.created_at
        if created_at and created_at.tzinfo is not None:
            created_at = created_at.replace(tzinfo=None)

        # Count sessions that included this position since goal was created
        session_count = db.query(func.count(func.distinct(Entry.id))).join(
            Response, Response.entry_id == Entry.id
        ).join(
            Question, Response.question_id == Question.id
        ).filter(
            and_(
                Entry.user_id == current_user.id,
                Entry.date >= created_at,
                Question.question_text == 'Class Technique',
                Response.answer.like(f"{goal.position} - %")
            )
        ).scalar() or 0

        # Find last trained date for this position
        last_entry = db.query(func.max(Entry.date)).join(
            Response, Response.entry_id == Entry.id
        ).join(
            Question, Response.question_id == Question.id
        ).filter(
            and_(
                Entry.user_id == current_user.id,
                Entry.date >= created_at,
                Question.question_text == 'Class Technique',
                Response.answer.like(f"{goal.position} - %")
            )
        ).scalar()

        # Calculate weeks since goal created
        now = datetime.utcnow()
        days_elapsed = (now - created_at).days if created_at else 0
        weeks_elapsed = max(1, round(days_elapsed / 7, 1))

        # Calculate deadline info
        days_left = None
        total_days = None
        if goal.timeline_weeks:
            deadline = created_at + timedelta(weeks=goal.timeline_weeks)
            days_left = (deadline - now).days
            total_days = goal.timeline_weeks * 7

        # Calculate weekly streak: consecutive weeks (current → past) with at least 1 session
        current_week_start = get_week_start(date.today())
        streak = 0
        # Don't look further back than goal creation
        goal_start_date = created_at.date() if created_at else date.today()
        check_week = current_week_start
        while check_week >= goal_start_date:
            week_end = check_week + timedelta(days=6)
            week_sessions = db.query(func.count(func.distinct(Entry.id))).join(
                Response, Response.entry_id == Entry.id
            ).join(
                Question, Response.question_id == Question.id
            ).filter(
                and_(
                    Entry.user_id == current_user.id,
                    func.date(Entry.date) >= check_week,
                    func.date(Entry.date) <= week_end,
                    Question.question_text == 'Class Technique',
                    Response.answer.like(f"{goal.position} - %")
                )
            ).scalar() or 0
            if week_sessions > 0:
                streak += 1
            else:
                break
            check_week -= timedelta(days=7)

        results.append({
            "id": goal.id,
            "position": goal.position,
            "notes": goal.notes,
            "timeline_weeks": goal.timeline_weeks,
            "created_at": goal.created_at.isoformat() if goal.created_at else None,
            "session_count": session_count,
            "weeks_elapsed": weeks_elapsed,
            "days_elapsed": days_elapsed,
            "days_left": days_left,
            "total_days": total_days,
            "last_trained": last_entry.isoformat() if last_entry else None,
            "sessions_per_week": round(session_count / weeks_elapsed, 1) if weeks_elapsed > 0 else 0,
            "weekly_streak": streak,
        })

    return results


@router.post("/techniques/{goal_id}/complete")
def complete_technique_goal(
    goal_id: int,
    data: TechniqueGoalComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete, archive, or extend a technique goal."""
    goal = db.query(TechniqueGoal).filter(
        and_(TechniqueGoal.id == goal_id, TechniqueGoal.user_id == current_user.id)
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Technique goal not found")

    if data.action == "complete":
        goal.is_active = False
        goal.status = "completed"
        goal.self_rating = data.self_rating
        goal.completed_at = datetime.utcnow()
        db.commit()
        return {"message": "Goal marked as completed", "status": "completed"}

    elif data.action == "archive":
        goal.is_active = False
        goal.status = "archived"
        goal.self_rating = data.self_rating
        goal.completed_at = datetime.utcnow()
        db.commit()
        return {"message": "Goal archived", "status": "archived"}

    elif data.action == "extend":
        if not data.extend_weeks or data.extend_weeks < 1:
            raise HTTPException(status_code=400, detail="extend_weeks must be at least 1")
        goal.timeline_weeks = (goal.timeline_weeks or 0) + data.extend_weeks
        db.commit()
        return {"message": f"Goal extended by {data.extend_weeks} weeks", "status": "active"}

    else:
        raise HTTPException(status_code=400, detail="action must be complete, archive, or extend")


@router.get("/techniques/expired")
def get_expired_technique_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active technique goals that have passed their deadline."""
    goals = db.query(TechniqueGoal).filter(
        and_(
            TechniqueGoal.user_id == current_user.id,
            TechniqueGoal.is_active == True,
            TechniqueGoal.timeline_weeks.isnot(None)
        )
    ).all()

    expired = []
    now = datetime.utcnow()
    for goal in goals:
        created = goal.created_at
        if created and created.tzinfo is not None:
            created = created.replace(tzinfo=None)
        if created and goal.timeline_weeks:
            deadline = created + timedelta(weeks=goal.timeline_weeks)
            if now > deadline:
                expired.append({
                    "id": goal.id,
                    "position": goal.position,
                    "timeline_weeks": goal.timeline_weeks,
                    "notes": goal.notes,
                    "created_at": goal.created_at.isoformat() if goal.created_at else None,
                    "days_overdue": (now - deadline).days,
                })

    return expired

@router.get("/techniques/history")
def get_technique_goals_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get completed/archived technique goals with session stats."""
    goals = db.query(TechniqueGoal).filter(
        and_(
            TechniqueGoal.user_id == current_user.id,
            TechniqueGoal.is_active == False,
            TechniqueGoal.status.in_(["completed", "archived"])
        )
    ).order_by(TechniqueGoal.completed_at.desc()).all()

    results = []
    for goal in goals:
        created = goal.created_at
        completed = goal.completed_at
        if created and created.tzinfo is not None:
            created = created.replace(tzinfo=None)
        if completed and completed.tzinfo is not None:
            completed = completed.replace(tzinfo=None)

        # Count sessions that included this position during the goal period
        end_date = completed or datetime.utcnow()
        session_count = db.query(func.count(func.distinct(Entry.id))).join(
            Response, Response.entry_id == Entry.id
        ).join(
            Question, Response.question_id == Question.id
        ).filter(
            and_(
                Entry.user_id == current_user.id,
                Entry.date >= created,
                Entry.date <= end_date,
                Question.question_text == 'Class Technique',
                Response.answer.like(f"{goal.position} - %")
            )
        ).scalar() or 0

        # Duration in weeks
        duration_days = (end_date - created).days if created else 0
        duration_weeks = round(duration_days / 7, 1)

        results.append({
            "id": goal.id,
            "position": goal.position,
            "notes": goal.notes,
            "timeline_weeks": goal.timeline_weeks,
            "status": goal.status,
            "self_rating": goal.self_rating,
            "session_count": session_count,
            "duration_weeks": duration_weeks,
            "duration_days": duration_days,
            "created_at": goal.created_at.isoformat() if goal.created_at else None,
            "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
        })

    return results

