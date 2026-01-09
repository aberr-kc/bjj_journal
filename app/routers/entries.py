from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Entry, Response, User
from app.schemas import Entry as EntrySchema, EntryCreate
from app.dependencies import get_current_user

router = APIRouter(prefix="/entries", tags=["entries"])

@router.post("/", response_model=EntrySchema)
def create_entry(
    entry: EntryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Create entry
        db_entry = Entry(
            user_id=current_user.id,
            date=entry.date,
            session_type=entry.session_type
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        # Create responses
        for response_data in entry.responses:
            db_response = Response(
                entry_id=db_entry.id,
                question_id=response_data.question_id,
                answer=response_data.answer
            )
            db.add(db_response)
        
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except Exception as e:
        print(f"Error creating entry: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating entry: {str(e)}")

@router.get("/", response_model=List[EntrySchema])
def get_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entries = db.query(Entry).filter(Entry.user_id == current_user.id).order_by(Entry.date.desc()).all()
    return entries

@router.get("/{entry_id}", response_model=EntrySchema)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(Entry).filter(
        Entry.id == entry_id, 
        Entry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{entry_id}", response_model=EntrySchema)
def update_entry(
    entry_id: int,
    entry: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get existing entry
    db_entry = db.query(Entry).filter(
        Entry.id == entry_id, 
        Entry.user_id == current_user.id
    ).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Update entry fields
    db_entry.date = entry.date
    db_entry.session_type = entry.session_type
    
    # Delete existing responses
    db.query(Response).filter(Response.entry_id == entry_id).delete()
    
    # Create new responses
    for response_data in entry.responses:
        db_response = Response(
            entry_id=db_entry.id,
            question_id=response_data.question_id,
            answer=response_data.answer
        )
        db.add(db_response)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/pending", response_model=List[EntrySchema])
def get_pending_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get entries that need journal completion"""
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        Entry.is_pending == True
    ).order_by(Entry.date.desc()).all()
    return entries

@router.put("/{entry_id}/complete", response_model=EntrySchema)
def complete_pending_entry(
    entry_id: int,
    entry: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a pending entry with journal responses"""
    # Get existing entry
    db_entry = db.query(Entry).filter(
        Entry.id == entry_id, 
        Entry.user_id == current_user.id,
        Entry.is_pending == True
    ).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Pending entry not found")
    
    # Update entry fields (keep Garmin data, update journal fields)
    db_entry.session_type = entry.session_type
    db_entry.is_pending = False
    
    # Delete existing responses and create new ones
    db.query(Response).filter(Response.entry_id == entry_id).delete()
    
    # Create new responses
    for response_data in entry.responses:
        db_response = Response(
            entry_id=db_entry.id,
            question_id=response_data.question_id,
            answer=response_data.answer
        )
        db.add(db_response)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(Entry).filter(
        Entry.id == entry_id, 
        Entry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted successfully"}