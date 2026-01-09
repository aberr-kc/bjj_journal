from pydantic import BaseModel
from datetime import datetime
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