"""
Session management endpoints with database persistence and guest support
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import time
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import GameSessionCRUD, ProblemCRUD
from app.services.problem_service import problem_service
from app.services.guest_service import GuestService
from app.services.auth_service import AuthService
from app.db.models import User
import random

router = APIRouter()


class SessionRequest(BaseModel):
    difficulty: str = "beginner"
    time_limit: Optional[int] = 900
    guest_id: Optional[str] = None  # For guest users


class SessionResponse(BaseModel):
    session_id: str
    difficulty: str
    time_limit: int
    problem_id: str
    problem_title: str
    problem_category: str
    code: str
    created_at: float
    user_type: str  # "authenticated", "guest", or "anonymous"


@router.post("/start", response_model=SessionResponse)
async def start_session(
    request: SessionRequest, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Start a new coding challenge session with support for authenticated, guest, and anonymous users"""
    
    # Validate difficulty
    if request.difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")
    
    # Determine user type and ID
    user_type = "anonymous"
    user_id = None
    current_user = None
    
    # Try to get authenticated user
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            current_user = AuthService.get_current_user(db, token)
        except Exception:
            pass
    
    if current_user:
        user_type = "authenticated"
        user_id = current_user.id
    elif request.guest_id:
        # Verify guest session exists
        guest_session = GuestService.get_guest_session(request.guest_id)
        if guest_session:
            user_type = "guest"
            user_id = request.guest_id
        else:
            raise HTTPException(status_code=404, detail="Guest session not found or expired")
    
    # Get problems from database first, fallback to problem service
    db_problems = ProblemCRUD.get_problems_by_difficulty(db, request.difficulty)
    
    if db_problems:
        # Use database problems
        selected_problem = random.choice(db_problems)
        problem_data = {
            'id': selected_problem.id,
            'title': selected_problem.title,
            'category': selected_problem.category,
            'code': selected_problem.code
        }
    else:
        # Fallback to problem service
        problem_data = problem_service.get_random_problem(request.difficulty)
        if not problem_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No problems available for difficulty: {request.difficulty}"
            )
    
    # Create session in database (only for authenticated users)
    session_id = f"session_{int(time.time())}"
    
    if user_type == "authenticated":
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "problem_id": problem_data['id'],
            "difficulty": request.difficulty,
            "time_limit": request.time_limit,
            "status": "active"
        }
        GameSessionCRUD.create_session(db, session_data)
    
    return SessionResponse(
        session_id=session_id,
        difficulty=request.difficulty,
        time_limit=request.time_limit,
        problem_id=problem_data['id'],
        problem_title=problem_data['title'],
        problem_category=problem_data['category'],
        code=problem_data['code'],
        created_at=time.time(),
        user_type=user_type
    )


@router.get("/status/{session_id}")
async def get_session_status(session_id: str, db: Session = Depends(get_db)):
    """Get session status from database (authenticated users only)"""
    
    session = GameSessionCRUD.get_session_by_id(db, session_id)
    if not session:
        # For guest/anonymous users, return basic status
        return {
            "session_id": session_id,
            "status": "active",
            "message": "Session status not tracked for guest/anonymous users"
        }
    
    # Calculate remaining time
    elapsed_time = (time.time() - session.started_at.timestamp()) if session.started_at else 0
    remaining_time = max(0, session.time_limit - int(elapsed_time))
    
    return {
        "session_id": session_id,
        "status": session.status,
        "remaining_time": remaining_time,
        "problem_id": session.problem_id,
        "difficulty": session.difficulty,
        "started_at": session.started_at.timestamp() if session.started_at else None
    }


@router.get("/history")
async def get_session_history(
    limit: int = 10, 
    guest_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get session history for authenticated users or guest users"""
    
    # Try to get authenticated user
    current_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            current_user = AuthService.get_current_user(db, token)
        except Exception:
            pass
    
    if current_user:
        # Authenticated user - get from database
        sessions = GameSessionCRUD.get_user_sessions(db, current_user.id, limit)
        
        session_history = []
        for session in sessions:
            session_history.append({
                "session_id": session.session_id,
                "problem_id": session.problem_id,
                "difficulty": session.difficulty,
                "status": session.status,
                "score": session.final_score,
                "started_at": session.started_at.timestamp() if session.started_at else None,
                "completed_at": session.completed_at.timestamp() if session.completed_at else None,
                "time_spent": session.time_spent
            })
        
        return {"sessions": session_history, "user_type": "authenticated"}
    
    elif guest_id:
        # Guest user - get from guest service
        guest_profile = GuestService.get_guest_profile(guest_id)
        return {
            "sessions": [],  # Guest sessions are not individually tracked
            "user_type": "guest",
            "summary": {
                "sessions_played": guest_profile["sessions_played"],
                "total_score": guest_profile["total_score"],
                "best_score": guest_profile["best_score"],
                "bugs_found": guest_profile["bugs_found"]
            },
            "message": "Individual session history not available for guest users. Consider registering to track detailed history."
        }
    
    else:
        return {
            "sessions": [], 
            "user_type": "anonymous",
            "message": "Session history requires authentication or guest session"
        }
