"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import session, submit, profile, explanation, auth, guest

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(guest.router, prefix="/guest", tags=["guest"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(submit.router, prefix="/submit", tags=["submit"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(explanation.router, prefix="/explanation", tags=["explanation"])
