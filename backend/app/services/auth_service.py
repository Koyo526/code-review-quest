"""
Authentication service for user registration and login
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.db.models import User
from app.db.crud import UserCRUD
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.SECRET_KEY or "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def register_user(db: Session, email: str, password: str, display_name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        
        # Check if user already exists
        existing_user = UserCRUD.get_user_by_email(db, email)
        if existing_user:
            return {
                "success": False,
                "error": "User with this email already exists"
            }
        
        # Generate username from email if not provided
        username = email.split('@')[0]
        
        # Check if username is taken, add suffix if needed
        base_username = username
        counter = 1
        while UserCRUD.get_user_by_username(db, username):
            username = f"{base_username}{counter}"
            counter += 1
        
        # Hash password
        hashed_password = AuthService.get_password_hash(password)
        
        try:
            # Create user
            user = UserCRUD.create_user(
                db=db,
                username=username,
                email=email,
                display_name=display_name or username,
                password_hash=hashed_password
            )
            
            # Create access token
            access_token = AuthService.create_access_token(
                data={"sub": user.id, "email": user.email}
            )
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create user: {str(e)}"
            }
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user with email and password"""
        
        # Get user by email
        user = UserCRUD.get_user_by_email(db, email)
        if not user:
            return {
                "success": False,
                "error": "Invalid email or password"
            }
        
        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return {
                "success": False,
                "error": "Invalid email or password"
            }
        
        # Update last login
        UserCRUD.update_user_stats(db, user.id, {"last_login": datetime.utcnow()})
        
        # Create access token
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "total_sessions": user.total_sessions,
                "total_score": user.total_score,
                "best_score": user.best_score
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = AuthService.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return UserCRUD.get_user_by_id(db, user_id)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
