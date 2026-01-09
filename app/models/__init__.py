from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    entries = relationship("Entry", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String)
    age = Column(Integer)
    weight = Column(Float)  # in kg
    height = Column(Float)  # in cm
    belt = Column(String)  # White, Blue, Purple, Brown, Black
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="profile")

class Entry(Base):
    __tablename__ = "entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    session_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="entries")
    responses = relationship("Response", back_populates="entry", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    category = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    
    responses = relationship("Response", back_populates="question")

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Text, nullable=False)
    
    entry = relationship("Entry", back_populates="responses")
    question = relationship("Question", back_populates="responses")