from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile
from app.dependencies import get_current_user
from app.schemas import UserProfileCreate, UserProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/", response_model=UserProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/", response_model=UserProfileResponse)
def create_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    profile = UserProfile(
        user_id=current_user.id,
        **profile_data.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.put("/", response_model=UserProfileResponse)
def update_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        # Create if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    for field, value in profile_data.dict().items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/exists")
def profile_exists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return {"exists": profile is not None}