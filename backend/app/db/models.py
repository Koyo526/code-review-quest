"""
Database models for Code Review Quest
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Added password hash
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # OAuth fields (for future use)
    github_id = Column(String(50), unique=True, nullable=True)
    google_id = Column(String(50), unique=True, nullable=True)
    
    # Profile stats
    total_sessions = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    total_bugs_found = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For email verification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions = relationship("GameSession", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")


class Problem(Base):
    """Problem model for storing coding challenges"""
    __tablename__ = "problems"
    
    id = Column(String, primary_key=True)  # e.g., "001_division_by_zero"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    category = Column(String(50), nullable=False)
    
    # Code and solution data
    code = Column(Text, nullable=False)
    bugs = Column(JSON, nullable=False)  # List of bug objects
    test_cases = Column(JSON, nullable=True)
    learning_objectives = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Statistics
    total_attempts = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    # Relationships
    sessions = relationship("GameSession", back_populates="problem")


class GameSession(Base):
    """Game session model for tracking individual play sessions"""
    __tablename__ = "game_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), unique=True, nullable=False)  # e.g., "session_1234567890"
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for guest users
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    
    # Session configuration
    difficulty = Column(String(20), nullable=False)
    time_limit = Column(Integer, nullable=False)  # in seconds
    
    # Session state
    status = Column(String(20), default="active")  # active, completed, expired
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, nullable=True)  # in seconds
    
    # Results (filled after submission)
    final_score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)
    bugs_found = Column(Integer, nullable=True)
    bugs_missed = Column(Integer, nullable=True)
    false_positives = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    problem = relationship("Problem", back_populates="sessions")
    submissions = relationship("Submission", back_populates="session")


class Submission(Base):
    """Submission model for storing bug reports and evaluations"""
    __tablename__ = "submissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Submission data
    bugs_reported = Column(JSON, nullable=False)  # List of reported bugs
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    
    # Evaluation results
    correct_bugs = Column(JSON, nullable=False)
    missed_bugs = Column(JSON, nullable=False)
    false_positives = Column(JSON, nullable=False)
    detailed_feedback = Column(JSON, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("GameSession", back_populates="submissions")
    user = relationship("User", back_populates="submissions")


class Badge(Base):
    """Badge definitions"""
    __tablename__ = "badges"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    
    # Requirements (JSON format for flexibility)
    requirements = Column(JSON, nullable=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    """User badge achievements"""
    __tablename__ = "user_badges"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    badge_id = Column(String, ForeignKey("badges.id"), nullable=False)
    
    # Achievement data
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    progress_data = Column(JSON, nullable=True)  # For tracking progress towards badge
    
    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")


class Leaderboard(Base):
    """Leaderboard entries for different time periods and categories"""
    __tablename__ = "leaderboard"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Leaderboard type and period
    board_type = Column(String(50), nullable=False)  # overall, weekly, monthly, category
    category = Column(String(50), nullable=True)  # difficulty or problem category
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Scores and stats
    total_score = Column(Integer, nullable=False)
    sessions_count = Column(Integer, nullable=False)
    average_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


# Index definitions for performance
from sqlalchemy import Index

# Indexes for common queries
Index('idx_user_username', User.username)
Index('idx_user_email', User.email)
Index('idx_session_user_id', GameSession.user_id)
Index('idx_session_problem_id', GameSession.problem_id)
Index('idx_session_status', GameSession.status)
Index('idx_submission_session_id', Submission.session_id)
Index('idx_submission_user_id', Submission.user_id)
Index('idx_leaderboard_type_period', Leaderboard.board_type, Leaderboard.period_start)
Index('idx_problem_difficulty', Problem.difficulty)
Index('idx_problem_category', Problem.category)
