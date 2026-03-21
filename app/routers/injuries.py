from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, InjuryLog
from app.schemas import InjuryLogCreate, InjuryLogResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/injuries", tags=["injuries"])

@router.post("/", response_model=InjuryLogResponse)
def create_injury(
    injury: InjuryLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_injury = InjuryLog(
        user_id=current_user.id,
        injured_area=injury.injured_area,
        injury_date=injury.injury_date,
        end_date=injury.end_date,
        cause=injury.cause,
        notes=injury.notes
    )
    db.add(new_injury)
    db.commit()
    db.refresh(new_injury)
    return new_injury

@router.get("/active", response_model=List[InjuryLogResponse])
def get_active_injuries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(InjuryLog).filter(
        InjuryLog.user_id == current_user.id,
        InjuryLog.end_date.is_(None)
    ).order_by(InjuryLog.injury_date.desc()).all()

@router.get("/", response_model=List[InjuryLogResponse])
def get_injuries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(InjuryLog).filter(InjuryLog.user_id == current_user.id).order_by(InjuryLog.injury_date.desc()).all()

@router.get("/{injury_id}", response_model=InjuryLogResponse)
def get_injury(
    injury_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    injury = db.query(InjuryLog).filter(
        InjuryLog.id == injury_id,
        InjuryLog.user_id == current_user.id
    ).first()
    if not injury:
        raise HTTPException(status_code=404, detail="Injury not found")
    return injury

@router.put("/{injury_id}", response_model=InjuryLogResponse)
def update_injury(
    injury_id: int,
    injury_data: InjuryLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    injury = db.query(InjuryLog).filter(
        InjuryLog.id == injury_id,
        InjuryLog.user_id == current_user.id
    ).first()
    if not injury:
        raise HTTPException(status_code=404, detail="Injury not found")
    
    injury.injured_area = injury_data.injured_area
    injury.injury_date = injury_data.injury_date
    injury.end_date = injury_data.end_date
    injury.cause = injury_data.cause
    injury.notes = injury_data.notes
    
    db.commit()
    db.refresh(injury)
    return injury

@router.delete("/{injury_id}")
def delete_injury(
    injury_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    injury = db.query(InjuryLog).filter(
        InjuryLog.id == injury_id,
        InjuryLog.user_id == current_user.id
    ).first()
    if not injury:
        raise HTTPException(status_code=404, detail="Injury not found")
    
    db.delete(injury)
    db.commit()
    return {"message": "Injury deleted successfully"}
