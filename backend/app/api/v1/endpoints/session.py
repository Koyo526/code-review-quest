"""
Session management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import time
from app.services.problem_service import problem_service

router = APIRouter()


class SessionRequest(BaseModel):
    difficulty: str = "beginner"
    time_limit: Optional[int] = 900


class SessionResponse(BaseModel):
    session_id: str
    difficulty: str
    time_limit: int
    problem_id: str
    problem_title: str
    problem_category: str
    code: str
    created_at: float


@router.post("/start", response_model=SessionResponse)
async def start_session(request: SessionRequest):
    """Start a new coding challenge session"""
    
    # Validate difficulty
    if request.difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")
    
    # Get a random problem for the specified difficulty
    problem = problem_service.get_random_problem(request.difficulty)
    
    if not problem:
        raise HTTPException(
            status_code=404, 
            detail=f"No problems available for difficulty: {request.difficulty}"
        )
    
    session_id = f"session_{int(time.time())}"
    
    return SessionResponse(
        session_id=session_id,
        difficulty=request.difficulty,
        time_limit=request.time_limit,
        problem_id=problem['id'],
        problem_title=problem['title'],
        problem_category=problem['category'],
        code=problem['code'],
        created_at=time.time()
    )


@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Get session status"""
    return {
        "session_id": session_id,
        "status": "active",
        "remaining_time": 850
    }
