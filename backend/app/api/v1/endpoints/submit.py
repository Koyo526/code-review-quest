"""
Code submission and evaluation endpoints with database persistence
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import time
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import GameSessionCRUD, SubmissionCRUD, ProblemCRUD, UserCRUD, BadgeCRUD
from app.services.problem_service import problem_service

router = APIRouter()


class BugReport(BaseModel):
    line_number: int
    description: Optional[str] = None


class SubmissionRequest(BaseModel):
    session_id: str
    problem_id: Optional[str] = None
    bugs: List[BugReport]


class SubmissionResponse(BaseModel):
    session_id: str
    problem_id: str
    score: int
    max_score: int
    correct_bugs: List[int]
    missed_bugs: List[int]
    false_positives: List[int]
    explanation: str
    detailed_feedback: List[dict]
    submitted_at: float
    badges_earned: List[dict] = []


@router.post("/", response_model=SubmissionResponse)
async def submit_solution(request: SubmissionRequest, db: Session = Depends(get_db)):
    """Submit bug findings for evaluation with database persistence"""
    
    # Get session from database
    session = GameSessionCRUD.get_session_by_id(db, request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Get problem data from database first, fallback to problem service
    problem_id = request.problem_id or session.problem_id
    db_problem = ProblemCRUD.get_problem_by_id(db, problem_id)
    
    if db_problem:
        problem = {
            'id': db_problem.id,
            'title': db_problem.title,
            'category': db_problem.category,
            'bugs': db_problem.bugs
        }
    else:
        # Fallback to problem service
        problem = problem_service.get_problem_by_id(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
    
    # Extract correct bug line numbers from problem data
    correct_bugs = [bug['line_number'] for bug in problem['bugs']]
    submitted_lines = [bug.line_number for bug in request.bugs]
    
    # Calculate results
    correct_bugs_found = [line for line in submitted_lines if line in correct_bugs]
    missed_bugs = [line for line in correct_bugs if line not in submitted_lines]
    false_positives = [line for line in submitted_lines if line not in correct_bugs]
    
    # Calculate score
    base_score = 100
    correct_points = len(correct_bugs_found) * (base_score // len(correct_bugs)) if correct_bugs else 0
    penalty = len(false_positives) * 10
    score = max(0, correct_points - penalty)
    
    # Generate detailed feedback
    detailed_feedback = _generate_detailed_feedback(
        problem, correct_bugs_found, missed_bugs, false_positives, request.bugs
    )
    
    # Generate explanation
    explanation = _generate_explanation(
        problem, len(correct_bugs_found), len(correct_bugs), 
        len(missed_bugs), len(false_positives), correct_points, penalty, score, base_score
    )
    
    # Calculate time spent
    time_spent = int(time.time() - session.started_at.timestamp()) if session.started_at else 0
    
    # Save submission to database
    submission_data = {
        "session_id": session.id,
        "user_id": session.user_id,
        "bugs_reported": [{"line_number": bug.line_number, "description": bug.description} for bug in request.bugs],
        "score": score,
        "max_score": base_score,
        "correct_bugs": correct_bugs_found,
        "missed_bugs": missed_bugs,
        "false_positives": false_positives,
        "detailed_feedback": detailed_feedback
    }
    
    submission = SubmissionCRUD.create_submission(db, submission_data)
    
    # Complete the session
    session_results = {
        "score": score,
        "max_score": base_score,
        "bugs_found": len(correct_bugs_found),
        "bugs_missed": len(missed_bugs),
        "false_positives": len(false_positives),
        "time_spent": time_spent
    }
    
    GameSessionCRUD.complete_session(db, request.session_id, session_results)
    
    # Update problem statistics
    ProblemCRUD.update_problem_stats(db, problem_id, score)
    
    # Update user statistics and check for badges
    badges_earned = []
    if session.user_id:
        # Update user stats
        user_stats = SubmissionCRUD.get_submission_stats(db, session.user_id)
        stats_update = {
            "total_sessions": user_stats["total_submissions"],
            "total_score": int(user_stats["average_score"] * user_stats["total_submissions"]),
            "best_score": user_stats["best_score"],
            "total_bugs_found": user_stats["total_bugs_found"],
            "accuracy_rate": user_stats["accuracy_rate"],
            "last_login": time.time()
        }
        
        UserCRUD.update_user_stats(db, session.user_id, stats_update)
        
        # Check for badge eligibility
        badges_earned = _check_and_award_badges(db, session.user_id, score, base_score, problem)
    
    return SubmissionResponse(
        session_id=request.session_id,
        problem_id=problem_id,
        score=score,
        max_score=base_score,
        correct_bugs=correct_bugs_found,
        missed_bugs=missed_bugs,
        false_positives=false_positives,
        explanation=explanation,
        detailed_feedback=detailed_feedback,
        submitted_at=time.time(),
        badges_earned=badges_earned
    )


def _generate_detailed_feedback(problem, correct_bugs_found, missed_bugs, false_positives, submitted_bugs):
    """Generate detailed feedback for each bug"""
    feedback = []
    
    # Feedback for correct bugs found
    for line_num in correct_bugs_found:
        bug_info = next((bug for bug in problem['bugs'] if bug['line_number'] == line_num), None)
        if bug_info:
            feedback.append({
                "line_number": line_num,
                "status": "correct",
                "message": f"✅ Correctly identified: {bug_info['description']}",
                "explanation": bug_info['explanation'],
                "type": bug_info['type'],
                "severity": bug_info['severity']
            })
    
    # Feedback for missed bugs
    for line_num in missed_bugs:
        bug_info = next((bug for bug in problem['bugs'] if bug['line_number'] == line_num), None)
        if bug_info:
            feedback.append({
                "line_number": line_num,
                "status": "missed",
                "message": f"❌ Missed bug: {bug_info['description']}",
                "explanation": bug_info['explanation'],
                "type": bug_info['type'],
                "severity": bug_info['severity'],
                "fix_suggestion": bug_info.get('fix_suggestion', '')
            })
    
    # Feedback for false positives
    for line_num in false_positives:
        submitted_bug = next((bug for bug in submitted_bugs if bug.line_number == line_num), None)
        feedback.append({
            "line_number": line_num,
            "status": "false_positive",
            "message": f"⚠️ False positive: No bug found at line {line_num}",
            "explanation": f"You reported: '{submitted_bug.description if submitted_bug and submitted_bug.description else 'No description'}', but this line appears to be correct.",
            "penalty": -10
        })
    
    return feedback


def _generate_explanation(problem, correct_count, total_bugs, missed_count, false_positive_count, 
                         correct_points, penalty, score, max_score):
    """Generate comprehensive explanation"""
    
    explanation_parts = [
        f"🎯 **{problem['title']} - Analysis Results**",
        f"**Problem Category:** {problem['category'].replace('_', ' ').title()}",
        "",
        f"**Bugs Found:** {correct_count}/{total_bugs}",
    ]
    
    # Add details about each bug type
    bug_types = {}
    for bug in problem['bugs']:
        bug_type = bug['type'].replace('_', ' ').title()
        if bug_type not in bug_types:
            bug_types[bug_type] = []
        bug_types[bug_type].append(f"Line {bug['line_number']}: {bug['description']}")
    
    for bug_type, bugs in bug_types.items():
        explanation_parts.append(f"**{bug_type} Issues:**")
        for bug in bugs:
            explanation_parts.append(f"  - {bug}")
    
    explanation_parts.extend([
        "",
        f"**Performance Summary:**",
        f"  - Correct identifications: {correct_count}",
        f"  - Missed bugs: {missed_count}",
        f"  - False positives: {false_positive_count}",
        "",
        f"**Score Calculation:**",
        f"  - Base points: {correct_points} (correct bugs × {100//total_bugs if total_bugs else 0})",
        f"  - Penalty: -{penalty} (false positives × 10)",
        f"  - Final score: {score}/{max_score}",
    ])
    
    # Add performance rating
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    if percentage >= 90:
        rating = "🏆 Excellent!"
    elif percentage >= 70:
        rating = "👍 Good job!"
    elif percentage >= 50:
        rating = "📈 Keep practicing!"
    else:
        rating = "💪 Room for improvement!"
    
    explanation_parts.extend([
        "",
        f"**Overall Rating:** {rating} ({percentage:.1f}%)"
    ])
    
    return "\n".join(explanation_parts)


def _check_and_award_badges(db: Session, user_id: str, score: int, max_score: int, problem: dict) -> List[dict]:
    """Check badge eligibility and award new badges"""
    badges_earned = []
    all_badges = BadgeCRUD.get_all_badges(db)
    
    for badge in all_badges:
        # Check if user already has this badge
        existing_badges = BadgeCRUD.get_user_badges(db, user_id)
        if any(ub.badge_id == badge.id for ub in existing_badges):
            continue
        
        # Check eligibility
        if BadgeCRUD.check_badge_eligibility(db, user_id, badge.requirements):
            # Award the badge
            user_badge = BadgeCRUD.award_badge(db, user_id, badge.id)
            badges_earned.append({
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "earned_at": user_badge.earned_at.timestamp()
            })
    
    return badges_earned
