from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, Integer
from datetime import date, datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models import User, UserGoal, WeeklyProgress, StreakHistory, Entry
from app.schemas import UserGoalCreate, UserGoal as UserGoalSchema, WeeklyProgressCreate, WeeklyProgress as WeeklyProgressSchema, StreakHistory as StreakHistorySchema, CurrentStreakResponse
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