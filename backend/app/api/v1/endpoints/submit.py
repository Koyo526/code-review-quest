"""
Code submission and evaluation endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time
import re
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


@router.post("/", response_model=SubmissionResponse)
async def submit_solution(request: SubmissionRequest):
    """Submit bug findings for evaluation"""
    
    # Extract problem_id from session_id if not provided
    problem_id = request.problem_id
    if not problem_id:
        # Try to extract from session (this is a simplified approach)
        # In a real app, you'd store session data in a database
        problem_id = "001_division_by_zero"  # Default fallback
    
    # Get the problem data
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
        submitted_at=time.time()
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
        f"**Difficulty:** {problem['difficulty'].title()}",
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
