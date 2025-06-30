"""
User profile management endpoints with guest support
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import GameSessionCRUD
from app.services.guest_service import GuestService
from app.services.auth_service import AuthService
from app.db.models import User

router = APIRouter()


class ProfileResponse(BaseModel):
    user_type: str  # "authenticated", "guest", or "anonymous"
    profile: Dict[str, Any]


@router.get("/stats", response_model=ProfileResponse)
async def get_profile_stats(
    guest_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get user profile statistics with support for authenticated, guest, and anonymous users"""
    
    # Try to get authenticated user
    current_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            current_user = AuthService.get_current_user(db, token)
        except Exception:
            pass
    
    if current_user:
        # Authenticated user - get comprehensive stats from database
        sessions = GameSessionCRUD.get_user_sessions(db, current_user.id, limit=100)
        
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == "completed"])
        total_score = sum([s.final_score or 0 for s in sessions])
        best_score = max([s.final_score or 0 for s in sessions]) if sessions else 0
        
        # Calculate average time and difficulty distribution
        completed_times = [s.time_spent for s in sessions if s.time_spent]
        avg_completion_time = sum(completed_times) / len(completed_times) if completed_times else 0
        
        difficulty_stats = {}
        for session in sessions:
            diff = session.difficulty
            if diff not in difficulty_stats:
                difficulty_stats[diff] = {"played": 0, "completed": 0}
            difficulty_stats[diff]["played"] += 1
            if session.status == "completed":
                difficulty_stats[diff]["completed"] += 1
        
        profile_data = {
            "user_id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "is_verified": current_user.is_verified,
            "member_since": current_user.created_at.isoformat() if current_user.created_at else None,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "total_score": total_score,
            "best_score": best_score,
            "average_score": (total_score / completed_sessions) if completed_sessions > 0 else 0,
            "average_completion_time": round(avg_completion_time, 2),
            "difficulty_breakdown": difficulty_stats,
            "achievements": _calculate_achievements(sessions),
            "recent_activity": _get_recent_activity(sessions[:5])
        }
        
        return ProfileResponse(user_type="authenticated", profile=profile_data)
    
    elif guest_id:
        # Guest user - get stats from guest service
        guest_profile = GuestService.get_guest_profile(guest_id)
        if not guest_profile:
            raise HTTPException(status_code=404, detail="Guest session not found or expired")
        
        profile_data = {
            "guest_id": guest_id,
            "session_started": guest_profile["created_at"],
            "sessions_played": guest_profile["sessions_played"],
            "total_score": guest_profile["total_score"],
            "best_score": guest_profile["best_score"],
            "bugs_found": guest_profile["bugs_found"],
            "time_played": guest_profile["time_played"],
            "favorite_difficulty": guest_profile["favorite_difficulty"],
            "achievements": guest_profile["achievements"],
            "registration_suggestion": {
                "message": "Register to save your progress permanently and unlock advanced features!",
                "benefits": [
                    "Permanent progress tracking",
                    "Detailed session history",
                    "Advanced statistics",
                    "Achievement system",
                    "Leaderboards",
                    "Custom difficulty settings"
                ]
            }
        }
        
        return ProfileResponse(user_type="guest", profile=profile_data)
    
    else:
        # Anonymous user
        profile_data = {
            "message": "Create a guest session or register to track your progress",
            "features_available": [
                "Play coding challenges",
                "Basic scoring",
                "Immediate feedback"
            ],
            "features_with_registration": [
                "Progress tracking",
                "Session history",
                "Achievement system",
                "Detailed statistics",
                "Leaderboards"
            ]
        }
        
        return ProfileResponse(user_type="anonymous", profile=profile_data)


@router.get("/achievements")
async def get_achievements(
    guest_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get user achievements"""
    
    # Try to get authenticated user
    current_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            current_user = AuthService.get_current_user(db, token)
        except Exception:
            pass
    
    if current_user:
        # Authenticated user achievements
        sessions = GameSessionCRUD.get_user_sessions(db, current_user.id, limit=100)
        achievements = _calculate_achievements(sessions)
        return {"user_type": "authenticated", "achievements": achievements}
    
    elif guest_id:
        # Guest user achievements
        guest_profile = GuestService.get_guest_profile(guest_id)
        if not guest_profile:
            raise HTTPException(status_code=404, detail="Guest session not found")
        
        return {
            "user_type": "guest", 
            "achievements": guest_profile["achievements"],
            "note": "Register to unlock more achievements and track them permanently!"
        }
    
    else:
        return {
            "user_type": "anonymous",
            "achievements": [],
            "message": "Start a session to begin earning achievements"
        }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get leaderboard (authenticated users only for privacy)"""
    
    # Get top performers from database
    sessions = GameSessionCRUD.get_top_sessions(db, limit=limit, difficulty=difficulty)
    
    leaderboard = []
    for session in sessions:
        if session.user and session.user.username:  # Only show users who opted in
            leaderboard.append({
                "rank": len(leaderboard) + 1,
                "username": session.user.username,
                "score": session.final_score,
                "difficulty": session.difficulty,
                "completion_time": session.time_spent,
                "date": session.completed_at.isoformat() if session.completed_at else None
            })
    
    return {
        "leaderboard": leaderboard,
        "note": "Only registered users appear on leaderboards. Register to compete!"
    }


def _calculate_achievements(sessions):
    """Calculate achievements based on session data"""
    achievements = []
    
    if not sessions:
        return achievements
    
    completed_sessions = [s for s in sessions if s.status == "completed"]
    total_score = sum([s.final_score or 0 for s in sessions])
    
    # First completion
    if completed_sessions:
        achievements.append({
            "name": "First Success",
            "description": "Completed your first coding challenge",
            "earned": True,
            "date": completed_sessions[0].completed_at.isoformat() if completed_sessions[0].completed_at else None
        })
    
    # Score milestones
    if total_score >= 100:
        achievements.append({
            "name": "Century Club",
            "description": "Earned 100+ total points",
            "earned": True
        })
    
    if total_score >= 500:
        achievements.append({
            "name": "High Scorer",
            "description": "Earned 500+ total points",
            "earned": True
        })
    
    # Session milestones
    if len(completed_sessions) >= 5:
        achievements.append({
            "name": "Persistent",
            "description": "Completed 5+ challenges",
            "earned": True
        })
    
    if len(completed_sessions) >= 20:
        achievements.append({
            "name": "Dedicated",
            "description": "Completed 20+ challenges",
            "earned": True
        })
    
    # Difficulty achievements
    difficulties = set([s.difficulty for s in completed_sessions])
    if "advanced" in difficulties:
        achievements.append({
            "name": "Expert Level",
            "description": "Completed an advanced challenge",
            "earned": True
        })
    
    if len(difficulties) >= 3:
        achievements.append({
            "name": "Well Rounded",
            "description": "Completed challenges at all difficulty levels",
            "earned": True
        })
    
    return achievements


def _get_recent_activity(recent_sessions):
    """Get recent activity summary"""
    activity = []
    
    for session in recent_sessions:
        activity.append({
            "session_id": session.session_id,
            "difficulty": session.difficulty,
            "status": session.status,
            "score": session.final_score,
            "date": session.started_at.isoformat() if session.started_at else None
        })
    
    return activity
