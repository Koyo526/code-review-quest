"""
Authentication endpoints for user registration and login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.db.models import User

router = APIRouter()
security = HTTPBearer()


# Request/Response Models
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str]
    total_sessions: int
    total_score: int
    best_score: int
    total_bugs_found: int
    accuracy_rate: float
    is_verified: bool
    created_at: Optional[str]


class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    error: Optional[str] = None


class PasswordValidationResponse(BaseModel):
    valid: bool
    errors: list[str]


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Optional dependency for current user (doesn't raise error if not authenticated)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return AuthService.get_current_user(db, token)
    except Exception:
        # If token is invalid or expired, return None instead of raising error
        return None


@router.post("/register", response_model=AuthResponse)
async def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Validate email format
    if not AuthService.validate_email(request.email):
        return AuthResponse(
            success=False,
            error="Invalid email format"
        )
    
    # Validate password strength
    password_validation = AuthService.validate_password(request.password)
    if not password_validation["valid"]:
        return AuthResponse(
            success=False,
            error="Password validation failed: " + "; ".join(password_validation["errors"])
        )
    
    # Register user
    result = AuthService.register_user(
        db=db,
        email=request.email,
        password=request.password,
        display_name=request.display_name
    )
    
    if not result["success"]:
        return AuthResponse(
            success=False,
            error=result["error"]
        )
    
    user_data = result["user"]
    return AuthResponse(
        success=True,
        user=UserResponse(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            total_sessions=0,
            total_score=0,
            best_score=0,
            total_bugs_found=0,
            accuracy_rate=0.0,
            is_verified=False,
            created_at=user_data["created_at"]
        ),
        access_token=result["access_token"],
        token_type=result["token_type"]
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user with email and password"""
    
    result = AuthService.authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )
    
    if not result["success"]:
        return AuthResponse(
            success=False,
            error=result["error"]
        )
    
    user_data = result["user"]
    return AuthResponse(
        success=True,
        user=UserResponse(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            total_sessions=user_data["total_sessions"],
            total_score=user_data["total_score"],
            best_score=user_data["best_score"],
            total_bugs_found=user_data.get("total_bugs_found", 0),
            accuracy_rate=user_data.get("accuracy_rate", 0.0),
            is_verified=False,
            created_at=None
        ),
        access_token=result["access_token"],
        token_type=result["token_type"]
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        total_sessions=current_user.total_sessions,
        total_score=current_user.total_score,
        best_score=current_user.best_score,
        total_bugs_found=current_user.total_bugs_found,
        accuracy_rate=current_user.accuracy_rate,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )


@router.post("/validate-password", response_model=PasswordValidationResponse)
async def validate_password(password: str):
    """Validate password strength"""
    result = AuthService.validate_password(password)
    return PasswordValidationResponse(
        valid=result["valid"],
        errors=result["errors"]
    )


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return {
        "success": True,
        "message": "Successfully logged out"
    }


@router.get("/check-email/{email}")
async def check_email_availability(email: str, db: Session = Depends(get_db)):
    """Check if email is available for registration"""
    from app.db.crud import UserCRUD
    
    existing_user = UserCRUD.get_user_by_email(db, email)
    return {
        "available": existing_user is None,
        "message": "Email is available" if existing_user is None else "Email is already registered"
    }
