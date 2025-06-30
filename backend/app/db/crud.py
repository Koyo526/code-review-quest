"""
CRUD operations for database models
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from app.db.models import (
    User, Problem, GameSession, Submission, Badge, UserBadge, Leaderboard
)


# User CRUD operations
class UserCRUD:
    @staticmethod
    def create_user(db: Session, username: str, email: str, password_hash: str, **kwargs) -> User:
        """Create a new user"""
        user = User(
            username=username, 
            email=email, 
            password_hash=password_hash,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user_stats(db: Session, user_id: str, stats_update: Dict[str, Any]) -> User:
        """Update user statistics"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in stats_update.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def update_user_profile(db: Session, user_id: str, profile_data: Dict[str, Any]) -> User:
        """Update user profile information"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            allowed_fields = ['display_name', 'avatar_url']
            for key, value in profile_data.items():
                if key in allowed_fields and hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user


# Problem CRUD operations
class ProblemCRUD:
    @staticmethod
    def get_problem_by_id(db: Session, problem_id: str) -> Optional[Problem]:
        """Get problem by ID"""
        return db.query(Problem).filter(
            and_(Problem.id == problem_id, Problem.is_active == True)
        ).first()
    
    @staticmethod
    def get_problems_by_difficulty(db: Session, difficulty: str) -> List[Problem]:
        """Get problems by difficulty"""
        return db.query(Problem).filter(
            and_(Problem.difficulty == difficulty, Problem.is_active == True)
        ).all()
    
    @staticmethod
    def get_problems_by_category(db: Session, category: str) -> List[Problem]:
        """Get problems by category"""
        return db.query(Problem).filter(
            and_(Problem.category == category, Problem.is_active == True)
        ).all()
    
    @staticmethod
    def get_all_problems(db: Session) -> List[Problem]:
        """Get all active problems"""
        return db.query(Problem).filter(Problem.is_active == True).all()
    
    @staticmethod
    def update_problem_stats(db: Session, problem_id: str, score: int):
        """Update problem statistics after a submission"""
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if problem:
            problem.total_attempts += 1
            if score > 0:
                problem.total_completions += 1
            
            # Update average score
            if problem.total_attempts > 0:
                current_total = problem.average_score * (problem.total_attempts - 1)
                problem.average_score = (current_total + score) / problem.total_attempts
            
            db.commit()


# GameSession CRUD operations
class GameSessionCRUD:
    @staticmethod
    def create_session(db: Session, session_data: Dict[str, Any]) -> GameSession:
        """Create a new game session"""
        session = GameSession(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session_by_id(db: Session, session_id: str) -> Optional[GameSession]:
        """Get session by session_id"""
        return db.query(GameSession).filter(GameSession.session_id == session_id).first()
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: str, limit: int = 10) -> List[GameSession]:
        """Get user's recent sessions"""
        return db.query(GameSession).filter(
            GameSession.user_id == user_id
        ).order_by(desc(GameSession.started_at)).limit(limit).all()
    
    @staticmethod
    def complete_session(db: Session, session_id: str, results: Dict[str, Any]) -> GameSession:
        """Mark session as completed with results"""
        session = db.query(GameSession).filter(GameSession.session_id == session_id).first()
        if session:
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.time_spent = results.get('time_spent')
            session.final_score = results.get('score')
            session.max_score = results.get('max_score')
            session.bugs_found = results.get('bugs_found')
            session.bugs_missed = results.get('bugs_missed')
            session.false_positives = results.get('false_positives')
            db.commit()
            db.refresh(session)
        return session


# Submission CRUD operations
class SubmissionCRUD:
    @staticmethod
    def create_submission(db: Session, submission_data: Dict[str, Any]) -> Submission:
        """Create a new submission"""
        submission = Submission(**submission_data)
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    
    @staticmethod
    def get_user_submissions(db: Session, user_id: str, limit: int = 10) -> List[Submission]:
        """Get user's recent submissions"""
        return db.query(Submission).filter(
            Submission.user_id == user_id
        ).order_by(desc(Submission.submitted_at)).limit(limit).all()
    
    @staticmethod
    def get_submission_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """Get user's submission statistics"""
        submissions = db.query(Submission).filter(Submission.user_id == user_id).all()
        
        if not submissions:
            return {
                "total_submissions": 0,
                "average_score": 0.0,
                "best_score": 0,
                "total_bugs_found": 0,
                "accuracy_rate": 0.0
            }
        
        total_score = sum(s.score for s in submissions)
        total_bugs_found = sum(len(s.correct_bugs) for s in submissions)
        total_possible_bugs = sum(len(s.correct_bugs) + len(s.missed_bugs) for s in submissions)
        
        return {
            "total_submissions": len(submissions),
            "average_score": total_score / len(submissions),
            "best_score": max(s.score for s in submissions),
            "total_bugs_found": total_bugs_found,
            "accuracy_rate": total_bugs_found / total_possible_bugs if total_possible_bugs > 0 else 0.0
        }


# Badge CRUD operations
class BadgeCRUD:
    @staticmethod
    def get_all_badges(db: Session) -> List[Badge]:
        """Get all active badges"""
        return db.query(Badge).filter(Badge.is_active == True).all()
    
    @staticmethod
    def get_user_badges(db: Session, user_id: str) -> List[UserBadge]:
        """Get user's earned badges"""
        return db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    
    @staticmethod
    def award_badge(db: Session, user_id: str, badge_id: str) -> UserBadge:
        """Award a badge to a user"""
        # Check if user already has this badge
        existing = db.query(UserBadge).filter(
            and_(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        ).first()
        
        if existing:
            return existing
        
        user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
        db.add(user_badge)
        db.commit()
        db.refresh(user_badge)
        return user_badge
    
    @staticmethod
    def check_badge_eligibility(db: Session, user_id: str, badge_requirements: Dict[str, Any]) -> bool:
        """Check if user meets badge requirements"""
        user_stats = SubmissionCRUD.get_submission_stats(db, user_id)
        user = UserCRUD.get_user_by_id(db, user_id)
        
        if not user:
            return False
        
        # Check each requirement
        for requirement, threshold in badge_requirements.items():
            if requirement == "bugs_found":
                if user.total_bugs_found < threshold:
                    return False
            elif requirement == "perfect_scores":
                perfect_scores = db.query(Submission).filter(
                    and_(Submission.user_id == user_id, Submission.score == Submission.max_score)
                ).count()
                if perfect_scores < threshold:
                    return False
            elif requirement == "challenges_completed":
                if user.total_sessions < threshold:
                    return False
            elif requirement == "security_problems_completed":
                security_completions = db.query(GameSession).join(Problem).filter(
                    and_(
                        GameSession.user_id == user_id,
                        GameSession.status == "completed",
                        Problem.category == "security"
                    )
                ).count()
                if security_completions < threshold:
                    return False
            elif requirement == "advanced_completed":
                advanced_completions = db.query(GameSession).filter(
                    and_(
                        GameSession.user_id == user_id,
                        GameSession.status == "completed",
                        GameSession.difficulty == "advanced"
                    )
                ).count()
                if advanced_completions < threshold:
                    return False
            elif requirement == "fastest_completion":
                fastest = db.query(func.min(GameSession.time_spent)).filter(
                    and_(GameSession.user_id == user_id, GameSession.status == "completed")
                ).scalar()
                if not fastest or fastest > threshold:
                    return False
        
        return True


# Leaderboard CRUD operations
class LeaderboardCRUD:
    @staticmethod
    def get_global_leaderboard(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get global leaderboard"""
        results = db.query(
            User.username,
            User.display_name,
            User.total_score,
            User.total_sessions,
            User.accuracy_rate
        ).filter(
            User.total_sessions > 0
        ).order_by(desc(User.total_score)).limit(limit).all()
        
        leaderboard = []
        for rank, result in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "username": result.display_name or result.username,
                "score": result.total_score,
                "sessions": result.total_sessions,
                "accuracy": result.accuracy_rate
            })
        
        return leaderboard
    
    @staticmethod
    def get_weekly_leaderboard(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get weekly leaderboard"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        results = db.query(
            User.username,
            User.display_name,
            func.sum(Submission.score).label('weekly_score'),
            func.count(Submission.id).label('weekly_submissions')
        ).join(Submission).filter(
            Submission.submitted_at >= week_ago
        ).group_by(User.id, User.username, User.display_name).order_by(
            desc('weekly_score')
        ).limit(limit).all()
        
        leaderboard = []
        for rank, result in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "username": result.display_name or result.username,
                "score": result.weekly_score,
                "submissions": result.weekly_submissions
            })
        
        return leaderboard
