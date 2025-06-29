"""
User profile and statistics endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
import time

router = APIRouter()


class Badge(BaseModel):
    id: str
    name: str
    description: str
    earned_at: float


class ProfileStats(BaseModel):
    total_sessions: int
    average_score: float
    best_score: int
    total_bugs_found: int
    accuracy_rate: float
    favorite_difficulty: str


class ProfileResponse(BaseModel):
    user_id: str
    username: str
    stats: ProfileStats
    badges: List[Badge]
    recent_scores: List[int]


@router.get("/me", response_model=ProfileResponse)
async def get_profile():
    """Get user profile and statistics"""
    
    # Sample data (will be replaced with database queries)
    sample_badges = [
        Badge(
            id="first_bug",
            name="First Bug Hunter",
            description="Found your first bug!",
            earned_at=time.time() - 86400
        ),
        Badge(
            id="perfect_score",
            name="Perfect Score",
            description="Achieved 100% accuracy",
            earned_at=time.time() - 3600
        )
    ]
    
    sample_stats = ProfileStats(
        total_sessions=15,
        average_score=78.5,
        best_score=100,
        total_bugs_found=42,
        accuracy_rate=0.85,
        favorite_difficulty="intermediate"
    )
    
    return ProfileResponse(
        user_id="user_123",
        username="CodeReviewer",
        stats=sample_stats,
        badges=sample_badges,
        recent_scores=[85, 92, 78, 100, 88]
    )


@router.get("/leaderboard")
async def get_leaderboard():
    """Get global leaderboard"""
    return {
        "leaderboard": [
            {"rank": 1, "username": "BugMaster", "score": 2450},
            {"rank": 2, "username": "CodeNinja", "score": 2380},
            {"rank": 3, "username": "ReviewPro", "score": 2290},
            {"rank": 4, "username": "CodeReviewer", "score": 1890},
            {"rank": 5, "username": "DebugKing", "score": 1750},
        ]
    }
