from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPCredentials
from sqlalchemy.orm import Session
from admin.database import SessionLocal
from admin.core.security import decode_token
from admin.models import User
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
def get_current_user(
    credentials: HTTPCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except HTTPException:
        raise