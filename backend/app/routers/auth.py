from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from ..database import get_db
from ..models import User, Portfolio
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)

router = APIRouter()

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    confirm_password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/signup", response_model=Token)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create new user
    new_user = User(email=user_data.email, hashed_password=get_password_hash(user_data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-create default portfolio for new user
    default_portfolio = Portfolio(
        name="My Portfolio",
        user_id=new_user.id
    )
    db.add(default_portfolio)
    db.commit()
    
    access_token = create_access_token(data={"user_id": new_user.id, "email": new_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": new_user.id, "email": new_user.email, "created_at": new_user.created_at.isoformat()}
    }

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "created_at": user.created_at.isoformat()}
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }