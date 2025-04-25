# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.models import User, UserRole
from app.auth.dependencies import create_access_token, get_current_user
from app.email.utils import send_verification_email
from app.utils.security import get_password_hash, verify_password, create_verification_token, verify_token
from pydantic import BaseModel, EmailStr
from app.config import settings


router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=UserRole.CLIENT,
        is_active=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    verification_token = create_verification_token({"sub": user_in.email})
    verification_url = f"{settings.BASE_URL}/verify-email?token={verification_token}"
    print("Verification URL:", verification_url)

    # Send verification email
    background_tasks.add_task(
        send_verification_email, user_in.email, verification_url
    )
    
    return {"message": "User created. Please check your email for verification."}

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = verify_token(token)["sub"]
    except:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Email not verified")
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}