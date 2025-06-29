"""
Problem management service
"""

import json
import os
import random
from typing import List, Dict, Optional
from pathlib import Path

class ProblemService:
    def __init__(self):
        self.problems_dir = Path("/app/problems")
        self._problems_cache = {}
        self._load_problems()
    
    def _load_problems(self):
        """Load all problems from JSON files"""
        if not self.problems_dir.exists():
            # Fallback to relative path for development
            self.problems_dir = Path("problems")
        
        if not self.problems_dir.exists():
            print("Warning: Problems directory not found")
            return
        
        for problem_file in self.problems_dir.glob("*.json"):
            try:
                with open(problem_file, 'r', encoding='utf-8') as f:
                    problem_data = json.load(f)
                    self._problems_cache[problem_data['id']] = problem_data
                    print(f"Loaded problem: {problem_data['id']}")
            except Exception as e:
                print(f"Error loading problem {problem_file}: {e}")
    
    def get_problem_by_id(self, problem_id: str) -> Optional[Dict]:
        """Get a specific problem by ID"""
        return self._problems_cache.get(problem_id)
    
    def get_problems_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get all problems of a specific difficulty"""
        return [
            problem for problem in self._problems_cache.values()
            if problem.get('difficulty') == difficulty
        ]
    
    def get_random_problem(self, difficulty: str = None) -> Optional[Dict]:
        """Get a random problem, optionally filtered by difficulty"""
        if difficulty:
            problems = self.get_problems_by_difficulty(difficulty)
        else:
            problems = list(self._problems_cache.values())
        
        if not problems:
            return None
        
        return random.choice(problems)
    
    def get_all_problems(self) -> List[Dict]:
        """Get all available problems"""
        return list(self._problems_cache.values())
    
    def get_problem_stats(self) -> Dict:
        """Get statistics about available problems"""
        problems = list(self._problems_cache.values())
        
        stats = {
            'total': len(problems),
            'by_difficulty': {},
            'by_category': {}
        }
        
        for problem in problems:
            # Count by difficulty
            difficulty = problem.get('difficulty', 'unknown')
            stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1
            
            # Count by category
            category = problem.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        return stats

# Global instance
problem_service = ProblemService()
