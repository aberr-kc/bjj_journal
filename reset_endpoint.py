from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/reset-password/{username}/{new_password}")
def reset_user_password(username: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.hashed_password = hashed_password
    db.commit()
    
    return {"message": f"Password updated for {username}"}