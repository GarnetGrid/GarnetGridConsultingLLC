from __future__ import annotations
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Security, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import User

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "jgpt_super_secret_key_change_me_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

from fastapi.security import APIKeyHeader
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


# --- Password Utilities ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Token Utilities ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    # 1. Check API Key
    if api_key:
        from app.db.models import ApiKey
        h = hash_key(api_key)
        stored_key = db.query(ApiKey).filter(ApiKey.key_hash == h, ApiKey.is_active == True).first()
        if stored_key:
            # Return transient admin user for API key
            return User(id=0, email=f"apikey:{stored_key.name}", role="admin", is_active=True)

    # 2. Check JWT
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        # If no token and no valid API key
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def seed_default_user():
    """Seeds a default admin user if none exists."""
    db = SessionLocal()
    try:
        count = db.query(User).count()
        if count == 0:
            print("Seeding default admin user: admin@jgpt.com / admin")
            hashed_password = get_password_hash("admin")
            admin_user = User(
                email="admin@jgpt.com",
                hashed_password=hashed_password,
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user seeded successfully.")
    except Exception as e:
        print(f"Error seeding default user: {e}")
        db.rollback()
    finally:
        db.close()
