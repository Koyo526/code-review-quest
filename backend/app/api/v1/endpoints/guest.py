"""
Guest user management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.guest_service import GuestService

router = APIRouter()


class GuestSessionRequest(BaseModel):
    nickname: Optional[str] = None


class GuestSessionResponse(BaseModel):
    guest_id: str
    nickname: str
    expires_at: float
    message: str


class GuestUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    score: Optional[int] = None
    bugs_found: Optional[int] = None
    time_played: Optional[int] = None
    difficulty: Optional[str] = None


@router.post("/start", response_model=GuestSessionResponse)
async def start_guest_session(request: GuestSessionRequest):
    """Start a new guest session"""
    
    nickname = request.nickname or f"Guest_{GuestService._generate_guest_id()[:8]}"
    guest_id = GuestService.create_guest_session(nickname)
    
    guest_session = GuestService.get_guest_session(guest_id)
    
    return GuestSessionResponse(
        guest_id=guest_id,
        nickname=nickname,
        expires_at=guest_session["expires_at"],
        message="Guest session created! Your progress will be saved for 24 hours. Register to save permanently."
    )


@router.get("/session/{guest_id}")
async def get_guest_session(guest_id: str):
    """Get guest session information"""
    
    guest_session = GuestService.get_guest_session(guest_id)
    if not guest_session:
        raise HTTPException(status_code=404, detail="Guest session not found or expired")
    
    return {
        "guest_id": guest_id,
        "nickname": guest_session["nickname"],
        "created_at": guest_session["created_at"],
        "expires_at": guest_session["expires_at"],
        "is_active": True
    }


@router.put("/session/{guest_id}")
async def update_guest_session(guest_id: str, request: GuestUpdateRequest):
    """Update guest session data"""
    
    guest_session = GuestService.get_guest_session(guest_id)
    if not guest_session:
        raise HTTPException(status_code=404, detail="Guest session not found or expired")
    
    # Update nickname if provided
    if request.nickname:
        GuestService.update_guest_nickname(guest_id, request.nickname)
    
    # Update game statistics if provided
    if request.score is not None:
        GuestService.update_guest_score(guest_id, request.score)
    
    if request.bugs_found is not None:
        GuestService.update_guest_stats(guest_id, bugs_found=request.bugs_found)
    
    if request.time_played is not None:
        GuestService.update_guest_stats(guest_id, time_played=request.time_played)
    
    if request.difficulty:
        GuestService.update_guest_stats(guest_id, difficulty=request.difficulty)
    
    return {"message": "Guest session updated successfully"}


@router.get("/profile/{guest_id}")
async def get_guest_profile(guest_id: str):
    """Get guest user profile"""
    
    guest_profile = GuestService.get_guest_profile(guest_id)
    if not guest_profile:
        raise HTTPException(status_code=404, detail="Guest session not found or expired")
    
    return {
        "guest_id": guest_id,
        "profile": guest_profile,
        "registration_benefits": {
            "permanent_progress": "Never lose your achievements and statistics",
            "detailed_history": "Track every session with detailed analytics",
            "leaderboards": "Compete with other players globally",
            "advanced_features": "Unlock custom difficulty settings and more",
            "community": "Join the Code Review Quest community"
        }
    }


@router.delete("/session/{guest_id}")
async def end_guest_session(guest_id: str):
    """End a guest session (cleanup)"""
    
    guest_session = GuestService.get_guest_session(guest_id)
    if not guest_session:
        raise HTTPException(status_code=404, detail="Guest session not found or expired")
    
    # In a real implementation, you might want to offer data export
    # or migration to a registered account before deletion
    
    return {
        "message": "Guest session ended. Consider registering to save your progress!",
        "final_stats": GuestService.get_guest_profile(guest_id)
    }


@router.get("/convert/{guest_id}")
async def get_conversion_data(guest_id: str):
    """Get data for converting guest session to registered account"""
    
    guest_profile = GuestService.get_guest_profile(guest_id)
    if not guest_profile:
        raise HTTPException(status_code=404, detail="Guest session not found or expired")
    
    return {
        "guest_id": guest_id,
        "conversion_data": {
            "nickname": guest_profile["nickname"],
            "sessions_played": guest_profile["sessions_played"],
            "total_score": guest_profile["total_score"],
            "best_score": guest_profile["best_score"],
            "bugs_found": guest_profile["bugs_found"],
            "time_played": guest_profile["time_played"],
            "achievements": guest_profile["achievements"],
            "favorite_difficulty": guest_profile["favorite_difficulty"]
        },
        "message": "This data can be transferred to your new registered account"
    }
