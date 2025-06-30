"""
Guest user service for temporary session management
"""

import time
import uuid
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class GuestService:
    """Service for managing temporary guest user sessions"""
    
    # In-memory storage for guest sessions (in production, use Redis or similar)
    _guest_sessions: Dict[str, Dict[str, Any]] = {}
    
    # Session expiration time (24 hours)
    SESSION_DURATION = 24 * 60 * 60  # 24 hours in seconds
    
    @classmethod
    def create_guest_session(cls, nickname: str = None) -> str:
        """Create a new guest session"""
        guest_id = cls._generate_guest_id()
        current_time = time.time()
        
        if not nickname:
            nickname = f"Guest_{guest_id[:8]}"
        
        cls._guest_sessions[guest_id] = {
            "guest_id": guest_id,
            "nickname": nickname,
            "created_at": current_time,
            "expires_at": current_time + cls.SESSION_DURATION,
            "last_active": current_time,
            "sessions_played": 0,
            "total_score": 0,
            "best_score": 0,
            "bugs_found": 0,
            "time_played": 0,
            "favorite_difficulty": "beginner",
            "achievements": []
        }
        
        return guest_id
    
    @classmethod
    def get_guest_session(cls, guest_id: str) -> Optional[Dict[str, Any]]:
        """Get guest session if it exists and hasn't expired"""
        if guest_id not in cls._guest_sessions:
            return None
        
        session = cls._guest_sessions[guest_id]
        
        # Check if session has expired
        if time.time() > session["expires_at"]:
            del cls._guest_sessions[guest_id]
            return None
        
        # Update last active time
        session["last_active"] = time.time()
        return session
    
    @classmethod
    def get_guest_profile(cls, guest_id: str) -> Optional[Dict[str, Any]]:
        """Get guest user profile"""
        session = cls.get_guest_session(guest_id)
        if not session:
            return None
        
        return {
            "guest_id": guest_id,
            "nickname": session["nickname"],
            "created_at": session["created_at"],
            "sessions_played": session["sessions_played"],
            "total_score": session["total_score"],
            "best_score": session["best_score"],
            "bugs_found": session["bugs_found"],
            "time_played": session["time_played"],
            "favorite_difficulty": session["favorite_difficulty"],
            "achievements": session["achievements"]
        }
    
    @classmethod
    def update_guest_nickname(cls, guest_id: str, nickname: str) -> bool:
        """Update guest nickname"""
        session = cls.get_guest_session(guest_id)
        if not session:
            return False
        
        session["nickname"] = nickname
        return True
    
    @classmethod
    def update_guest_score(cls, guest_id: str, score: int) -> bool:
        """Update guest score and session count"""
        session = cls.get_guest_session(guest_id)
        if not session:
            return False
        
        session["sessions_played"] += 1
        session["total_score"] += score
        session["best_score"] = max(session["best_score"], score)
        
        # Update achievements based on score
        cls._update_guest_achievements(guest_id, session)
        
        return True
    
    @classmethod
    def update_guest_stats(cls, guest_id: str, **kwargs) -> bool:
        """Update various guest statistics"""
        session = cls.get_guest_session(guest_id)
        if not session:
            return False
        
        if "bugs_found" in kwargs:
            session["bugs_found"] += kwargs["bugs_found"]
        
        if "time_played" in kwargs:
            session["time_played"] += kwargs["time_played"]
        
        if "difficulty" in kwargs:
            # Simple logic to track favorite difficulty
            session["favorite_difficulty"] = kwargs["difficulty"]
        
        return True
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Remove expired guest sessions"""
        current_time = time.time()
        expired_sessions = [
            guest_id for guest_id, session in cls._guest_sessions.items()
            if current_time > session["expires_at"]
        ]
        
        for guest_id in expired_sessions:
            del cls._guest_sessions[guest_id]
        
        return len(expired_sessions)
    
    @classmethod
    def _generate_guest_id(cls) -> str:
        """Generate a unique guest ID"""
        return f"guest_{uuid.uuid4().hex}"
    
    @classmethod
    def _update_guest_achievements(cls, guest_id: str, session: Dict[str, Any]):
        """Update guest achievements based on current stats"""
        achievements = session["achievements"]
        
        # First session achievement
        if session["sessions_played"] == 1 and "first_session" not in [a["id"] for a in achievements]:
            achievements.append({
                "id": "first_session",
                "name": "First Steps",
                "description": "Completed your first coding challenge as a guest",
                "earned_at": time.time()
            })
        
        # Score milestones
        if session["total_score"] >= 50 and "score_50" not in [a["id"] for a in achievements]:
            achievements.append({
                "id": "score_50",
                "name": "Getting Started",
                "description": "Earned 50+ points as a guest",
                "earned_at": time.time()
            })
        
        if session["total_score"] >= 100 and "score_100" not in [a["id"] for a in achievements]:
            achievements.append({
                "id": "score_100",
                "name": "Century Guest",
                "description": "Earned 100+ points as a guest",
                "earned_at": time.time()
            })
        
        # Session count milestones
        if session["sessions_played"] >= 3 and "sessions_3" not in [a["id"] for a in achievements]:
            achievements.append({
                "id": "sessions_3",
                "name": "Getting Hooked",
                "description": "Played 3+ sessions as a guest",
                "earned_at": time.time()
            })
        
        if session["sessions_played"] >= 5 and "sessions_5" not in [a["id"] for a in achievements]:
            achievements.append({
                "id": "sessions_5",
                "name": "Regular Guest",
                "description": "Played 5+ sessions as a guest - time to register?",
                "earned_at": time.time()
            })
