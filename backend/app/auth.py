from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import TokenData

settings = get_settings()
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"DEBUG decode_token: token={token[:50]}...")
        print(f"DEBUG decode_token: secret={settings.JWT_SECRET_KEY}")
        print(f"DEBUG decode_token: algorithm={settings.JWT_ALGORITHM}")
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        print(f"DEBUG decode_token: payload={payload}")
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            print("DEBUG decode_token: user_id is None!")
            raise credentials_exception
        user_id: int = int(user_id_str)
        username: str = payload.get("username")
        role: str = payload.get("role")
        token_data = TokenData(user_id=user_id, username=username, role=role)
        print(f"DEBUG decode_token: Success! token_data={token_data}")
        return token_data
    except JWTError as e:
        print(f"DEBUG decode_token: JWTError={e}")
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        print(f"DEBUG: Received token: {token[:50]}...")
        token_data = decode_token(token)
        print(
            f"DEBUG: Token data: user_id={token_data.user_id}, username={token_data.username}"
        )
        user = db.query(User).filter(User.id == token_data.user_id).first()
        print(f"DEBUG: User found: {user}")
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
    except Exception as e:
        print(f"DEBUG: Error in get_current_user: {e}")
        raise


async def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def get_current_staff_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require staff or admin role"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff or admin access required",
        )
    return current_user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None if not (no error thrown)"""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        token_data = decode_token(token)
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if user and user.is_active:
            return user
        return None
    except:
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
