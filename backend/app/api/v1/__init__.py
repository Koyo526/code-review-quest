"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import session, submit, profile

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(submit.router, prefix="/submit", tags=["submit"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
