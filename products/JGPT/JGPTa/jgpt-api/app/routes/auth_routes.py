from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import User
from app.util.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    get_db,
)
from pydantic import BaseModel, EmailStr
import secrets
from app.db.models import ApiKey
from app.util.auth import hash_key, get_current_admin

router = APIRouter()

class UserCreate(BaseModel):
    model_config = {'extra': 'forbid'}
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if this is the first user (make them admin)
    count = db.query(User).count()
    role = "admin" if count == 0 else "viewer"
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

from fastapi import Request
from app.util.limiter import limiter

@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- API Key Management (Admin Only) ---

class ApiKeyCreate(BaseModel):
    model_config = {'extra': 'forbid'}
    name: str

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    prefix: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

class ApiKeyCreateResponse(BaseModel):
    """Response when creating a new API key - includes the full key ONCE"""
    id: int
    name: str
    prefix: str
    is_active: bool
    created_at: str
    full_key: str  # Only returned on creation

@router.post("/api-keys", response_model=ApiKeyCreateResponse)
def create_api_key(key_data: ApiKeyCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    # Generate key: jgpt_ + 32 chars hex
    raw_key = "jgpt_" + secrets.token_hex(32)
    h = hash_key(raw_key)
    
    new_key = ApiKey(
        key_hash=h,
        prefix=raw_key[:8] + "...",
        name=key_data.name,
        is_active=True
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    # Return the full key ONCE - user must save it
    return {
        "id": new_key.id,
        "name": new_key.name,
        "prefix": new_key.prefix,
        "is_active": new_key.is_active,
        "created_at": new_key.created_at.isoformat(),
        "full_key": raw_key
    }


@router.get("/api-keys", response_model=list[ApiKeyResponse])
def list_api_keys(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(ApiKey).all()

@router.delete("/api-keys/{key_id}")
def revoke_api_key(key_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    db.delete(key)
    db.commit()
    return {"ok": True}

