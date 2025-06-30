"""
Database initialization and seeding
"""

import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.db.models import Base, Problem, Badge, User
from app.services.problem_service import problem_service
import logging

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def seed_problems(db: Session):
    """Seed problems from JSON files"""
    logger.info("Seeding problems...")
    
    # Get all problems from problem service
    problems_data = problem_service.get_all_problems()
    
    for problem_data in problems_data:
        # Check if problem already exists
        existing_problem = db.query(Problem).filter(Problem.id == problem_data['id']).first()
        if existing_problem:
            logger.info(f"Problem {problem_data['id']} already exists, skipping...")
            continue
        
        # Create new problem
        problem = Problem(
            id=problem_data['id'],
            title=problem_data['title'],
            description=problem_data['description'],
            difficulty=problem_data['difficulty'],
            category=problem_data['category'],
            code=problem_data['code'],
            bugs=problem_data['bugs'],
            test_cases=problem_data.get('test_cases', []),
            learning_objectives=problem_data.get('learning_objectives', [])
        )
        
        db.add(problem)
        logger.info(f"Added problem: {problem_data['title']}")
    
    db.commit()
    logger.info("Problems seeded successfully")


def seed_badges(db: Session):
    """Seed initial badges"""
    logger.info("Seeding badges...")
    
    badges_data = [
        {
            "id": "first_bug",
            "name": "First Bug Hunter",
            "description": "Found your first bug!",
            "icon": "🐛",
            "category": "milestone",
            "requirements": {"bugs_found": 1}
        },
        {
            "id": "perfect_score",
            "name": "Perfect Score",
            "description": "Achieved 100% accuracy in a challenge",
            "icon": "🎯",
            "category": "achievement",
            "requirements": {"perfect_scores": 1}
        },
        {
            "id": "bug_master",
            "name": "Bug Master",
            "description": "Found 50 bugs across all challenges",
            "icon": "🏆",
            "category": "milestone",
            "requirements": {"bugs_found": 50}
        },
        {
            "id": "security_expert",
            "name": "Security Expert",
            "description": "Completed 5 security-related challenges",
            "icon": "🔒",
            "category": "expertise",
            "requirements": {"security_problems_completed": 5}
        },
        {
            "id": "speed_demon",
            "name": "Speed Demon",
            "description": "Completed a challenge in under 2 minutes",
            "icon": "⚡",
            "category": "achievement",
            "requirements": {"fastest_completion": 120}
        },
        {
            "id": "persistent_learner",
            "name": "Persistent Learner",
            "description": "Completed 10 challenges",
            "icon": "📚",
            "category": "milestone",
            "requirements": {"challenges_completed": 10}
        },
        {
            "id": "advanced_challenger",
            "name": "Advanced Challenger",
            "description": "Completed 3 advanced difficulty challenges",
            "icon": "🔥",
            "category": "difficulty",
            "requirements": {"advanced_completed": 3}
        }
    ]
    
    for badge_data in badges_data:
        # Check if badge already exists
        existing_badge = db.query(Badge).filter(Badge.id == badge_data['id']).first()
        if existing_badge:
            logger.info(f"Badge {badge_data['id']} already exists, skipping...")
            continue
        
        badge = Badge(
            id=badge_data['id'],
            name=badge_data['name'],
            description=badge_data['description'],
            icon=badge_data['icon'],
            category=badge_data['category'],
            requirements=badge_data['requirements']
        )
        
        db.add(badge)
        logger.info(f"Added badge: {badge_data['name']}")
    
    db.commit()
    logger.info("Badges seeded successfully")


def create_demo_user(db: Session):
    """Create a demo user for testing"""
    logger.info("Creating demo user...")
    
    # Check if demo user already exists
    existing_user = db.query(User).filter(User.username == "demo_user").first()
    if existing_user:
        logger.info("Demo user already exists, skipping...")
        return
    
    # Import auth service for password hashing
    from app.services.auth_service import AuthService
    
    # Create demo user with hashed password
    demo_password_hash = AuthService.get_password_hash("demo123456")
    
    demo_user = User(
        username="demo_user",
        email="demo@codereviewquest.com",
        password_hash=demo_password_hash,
        display_name="Demo User",
        total_sessions=15,
        total_score=1250,
        best_score=100,
        total_bugs_found=42,
        accuracy_rate=0.85,
        is_verified=True  # Demo user is pre-verified
    )
    
    db.add(demo_user)
    db.commit()
    logger.info("Demo user created successfully (username: demo_user, password: demo123456)")


def init_database():
    """Initialize the entire database"""
    logger.info("Initializing database...")
    
    try:
        # Create tables
        create_tables()
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Seed data
            seed_problems(db)
            seed_badges(db)
            create_demo_user(db)
            
            logger.info("Database initialization completed successfully!")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    init_database()
