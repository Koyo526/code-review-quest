"""
Code submission and evaluation endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time

router = APIRouter()


class BugReport(BaseModel):
    line_number: int
    description: Optional[str] = None


class SubmissionRequest(BaseModel):
    session_id: str
    bugs: List[BugReport]


class SubmissionResponse(BaseModel):
    session_id: str
    score: int
    max_score: int
    correct_bugs: List[int]
    missed_bugs: List[int]
    false_positives: List[int]
    explanation: str
    submitted_at: float


@router.post("/", response_model=SubmissionResponse)
async def submit_solution(request: SubmissionRequest):
    """Submit bug findings for evaluation"""
    
    # Sample correct answer (line 4 has division by zero bug)
    correct_bugs = [4]  # Line numbers with actual bugs
    
    submitted_lines = [bug.line_number for bug in request.bugs]
    
    # Calculate results
    correct_bugs_found = [line for line in submitted_lines if line in correct_bugs]
    missed_bugs = [line for line in correct_bugs if line not in submitted_lines]
    false_positives = [line for line in submitted_lines if line not in correct_bugs]
    
    # Calculate score
    base_score = 100
    correct_points = len(correct_bugs_found) * 50
    penalty = len(false_positives) * 10
    score = max(0, correct_points - penalty)
    
    explanation = f"""
    🎯 **Analysis Results:**
    
    **Correct Bugs Found:** {len(correct_bugs_found)}/{len(correct_bugs)}
    - Line 4: Division by zero when empty list is passed
    
    **Issues:**
    - Missed bugs: {len(missed_bugs)}
    - False positives: {len(false_positives)}
    
    **Score Calculation:**
    - Base points: {correct_points} (correct bugs × 50)
    - Penalty: -{penalty} (false positives × 10)
    - Final score: {score}/{base_score}
    """
    
    return SubmissionResponse(
        session_id=request.session_id,
        score=score,
        max_score=base_score,
        correct_bugs=correct_bugs_found,
        missed_bugs=missed_bugs,
        false_positives=false_positives,
        explanation=explanation.strip(),
        submitted_at=time.time()
    )
