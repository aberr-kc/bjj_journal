from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

# User schemas
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Question schemas
class Question(BaseModel):
    id: int
    question_text: str
    question_type: str
    category: str
    order_index: int
    
    class Config:
        from_attributes = True

# Response schemas
class ResponseCreate(BaseModel):
    question_id: int
    answer: str

class Response(BaseModel):
    id: int
    question_id: int
    answer: str
    question: Question
    
    class Config:
        from_attributes = True

# Entry schemas
class EntryCreate(BaseModel):
    date: datetime
    session_type: str
    responses: List[ResponseCreate]

class Entry(BaseModel):
    id: int
    date: datetime
    session_type: str
    injured_during_session: bool
    created_at: datetime
    updated_at: Optional[datetime]
    responses: List[Response]
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Profile schemas
class UserProfileCreate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    belt: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    age: Optional[int]
    weight: Optional[float]
    height: Optional[float]
    belt: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

# Goal schemas
class UserGoalCreate(BaseModel):
    weekly_sessions_target: int
    weekly_rounds_target: Optional[int] = None
    start_date: date

class UserGoal(BaseModel):
    id: int
    user_id: int
    weekly_sessions_target: int
    weekly_rounds_target: Optional[int]
    start_date: date
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class WeeklyProgressCreate(BaseModel):
    week_start_date: date
    is_paused: Optional[bool] = False

class WeeklyProgress(BaseModel):
    id: int
    user_id: int
    week_start_date: date
    sessions_completed: int
    goal_met: bool
    is_paused: bool
    streak_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StreakHistory(BaseModel):
    id: int
    user_id: int
    streak_length: int
    start_date: date
    end_date: Optional[date]
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CurrentStreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    current_week_progress: int
    current_week_goal: int
    weeks_until_goal: int
    current_week_rounds: Optional[int] = 0
    current_week_rounds_goal: Optional[int] = 0

class TechniqueGoalCreate(BaseModel):
    position: str
    notes: Optional[str] = None
    timeline_weeks: Optional[int] = None

class TechniqueGoalComplete(BaseModel):
    action: str  # "complete", "archive", "extend"
    self_rating: Optional[int] = None  # 1-5
    extend_weeks: Optional[int] = None

class TechniqueGoalResponse(BaseModel):
    id: int
    user_id: int
    position: str
    notes: Optional[str]
    timeline_weeks: Optional[int]
    is_active: bool
    status: Optional[str]
    self_rating: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class InjuryLogCreate(BaseModel):
    injured_area: str
    injury_date: date
    end_date: Optional[date] = None
    cause: str
    notes: Optional[str] = None

class InjuryLogResponse(BaseModel):
    id: int
    user_id: int
    injured_area: str
    injury_date: date
    end_date: Optional[date]
    cause: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True