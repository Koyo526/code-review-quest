"""
Problem explanation and solution endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.problem_service import problem_service

router = APIRouter()


class ExplanationResponse(BaseModel):
    problem_id: str
    title: str
    difficulty: str
    category: str
    description: str
    code: str
    bugs: List[Dict]
    test_cases: List[Dict]
    learning_objectives: List[str]
    detailed_explanation: str


@router.get("/problem/{problem_id}", response_model=ExplanationResponse)
async def get_problem_explanation(problem_id: str):
    """Get detailed explanation for a specific problem"""
    
    problem = problem_service.get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Generate detailed explanation
    detailed_explanation = _generate_detailed_explanation(problem)
    
    return ExplanationResponse(
        problem_id=problem['id'],
        title=problem['title'],
        difficulty=problem['difficulty'],
        category=problem['category'],
        description=problem['description'],
        code=problem['code'],
        bugs=problem['bugs'],
        test_cases=problem.get('test_cases', []),
        learning_objectives=problem.get('learning_objectives', []),
        detailed_explanation=detailed_explanation
    )


@router.get("/problems")
async def get_all_problems():
    """Get list of all available problems"""
    problems = problem_service.get_all_problems()
    
    # Return summary information
    return {
        "problems": [
            {
                "id": p['id'],
                "title": p['title'],
                "difficulty": p['difficulty'],
                "category": p['category'],
                "description": p['description']
            }
            for p in problems
        ]
    }


@router.get("/stats")
async def get_problem_stats():
    """Get statistics about available problems"""
    return problem_service.get_problem_stats()


def _generate_detailed_explanation(problem: Dict) -> str:
    """Generate a comprehensive explanation for the problem"""
    
    explanation_parts = []
    
    # Problem overview
    explanation_parts.append(f"## 🎯 Problem: {problem['title']}")
    explanation_parts.append(f"**Difficulty:** {problem['difficulty'].title()}")
    explanation_parts.append(f"**Category:** {problem['category'].replace('_', ' ').title()}")
    explanation_parts.append(f"\n{problem['description']}")
    
    # Bug analysis
    explanation_parts.append("\n## 🐛 Bug Analysis")
    for i, bug in enumerate(problem['bugs'], 1):
        explanation_parts.append(f"\n### Bug #{i} - Line {bug['line_number']}")
        explanation_parts.append(f"**Type:** {bug['type'].replace('_', ' ').title()}")
        explanation_parts.append(f"**Severity:** {bug['severity'].title()}")
        explanation_parts.append(f"**Description:** {bug['description']}")
        explanation_parts.append(f"**Explanation:** {bug['explanation']}")
        explanation_parts.append(f"**Fix Suggestion:** {bug['fix_suggestion']}")
    
    # Test cases
    if problem.get('test_cases'):
        explanation_parts.append("\n## 🧪 Test Cases")
        for i, test_case in enumerate(problem['test_cases'], 1):
            explanation_parts.append(f"\n### Test Case #{i}")
            if 'input' in test_case:
                explanation_parts.append(f"**Input:** {test_case['input']}")
            if 'expected_output' in test_case:
                explanation_parts.append(f"**Expected Output:** {test_case['expected_output']}")
            if 'expected_error' in test_case:
                explanation_parts.append(f"**Expected Error:** {test_case['expected_error']}")
            if 'expected_vulnerability' in test_case:
                explanation_parts.append(f"**Vulnerability:** {test_case['expected_vulnerability']}")
    
    # Learning objectives
    if problem.get('learning_objectives'):
        explanation_parts.append("\n## 📚 Learning Objectives")
        for objective in problem['learning_objectives']:
            explanation_parts.append(f"- {objective}")
    
    # Best practices
    explanation_parts.append("\n## ✅ Best Practices")
    explanation_parts.append(_get_best_practices_for_category(problem['category']))
    
    return "\n".join(explanation_parts)


def _get_best_practices_for_category(category: str) -> str:
    """Get best practices based on problem category"""
    
    practices = {
        'runtime_error': """
- Always validate input parameters
- Handle edge cases (empty collections, null values)
- Use defensive programming techniques
- Add proper error handling with try-catch blocks
        """,
        'logic_error': """
- Write comprehensive unit tests
- Use clear variable names and comments
- Break complex logic into smaller functions
- Test boundary conditions thoroughly
        """,
        'security': """
- Never trust user input
- Use parameterized queries for database operations
- Implement proper input validation and sanitization
- Follow the principle of least privilege
        """,
        'resource_management': """
- Always close resources explicitly
- Use context managers (with statements) when possible
- Implement proper exception handling
- Monitor resource usage in production
        """,
        'concurrency': """
- Use proper synchronization mechanisms (locks, semaphores)
- Avoid shared mutable state when possible
- Test concurrent code thoroughly
- Consider using thread-safe data structures
        """
    }
    
    return practices.get(category, "- Follow general coding best practices\n- Write clean, readable code\n- Test thoroughly")
