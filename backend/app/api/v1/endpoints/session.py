"""
Session management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

router = APIRouter()


class SessionRequest(BaseModel):
    difficulty: str = "beginner"
    time_limit: Optional[int] = 900


class SessionResponse(BaseModel):
    session_id: str
    difficulty: str
    time_limit: int
    problem_id: str
    code: str
    created_at: float


@router.post("/start", response_model=SessionResponse)
async def start_session(request: SessionRequest):
    """Start a new coding challenge session"""
    
    # Validate difficulty
    if request.difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")
    
    # Sample problem code (will be replaced with database lookup)
    sample_code = '''def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)  # Bug: Division by zero if empty list

# Test the function
result = calculate_average([1, 2, 3, 4, 5])
print(f"Average: {result}")'''
    
    session_id = f"session_{int(time.time())}"
    
    return SessionResponse(
        session_id=session_id,
        difficulty=request.difficulty,
        time_limit=request.time_limit,
        problem_id="001_division_by_zero",
        code=sample_code,
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
