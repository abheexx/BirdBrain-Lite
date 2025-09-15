import numpy as np
from typing import Dict, List, Tuple
from models import Exercise, Difficulty, BKTParams


class BayesianKnowledgeTracing:
    """Bayesian Knowledge Tracing implementation with latency adjustments."""
    
    def __init__(self):
        self.default_params = BKTParams()
    
    def update_posterior(self, p_known: float, correct: bool, latency_ms: int, 
                        params: BKTParams) -> float:
        """
        Update posterior probability of knowing a skill given correctness and latency.
        
        Args:
            p_known: Current probability of knowing the skill
            correct: Whether the answer was correct
            latency_ms: Time taken to answer in milliseconds
            params: BKT parameters for the skill
            
        Returns:
            Updated probability of knowing the skill
        """
        # Apply latency adjustments
        adjusted_correctness = self._adjust_for_latency(correct, latency_ms)
        
        if adjusted_correctness == 1.0:
            # Correct answer
            numerator = p_known * (1 - params.s)
            denominator = p_known * (1 - params.s) + (1 - p_known) * params.g
        else:
            # Incorrect answer
            numerator = p_known * params.s
            denominator = p_known * params.s + (1 - p_known) * (1 - params.g)
        
        if denominator == 0:
            return p_known  # Avoid division by zero
        
        return numerator / denominator
    
    def _adjust_for_latency(self, correct: bool, latency_ms: int) -> float:
        """
        Adjust correctness based on latency to account for guessing vs. mastery.
        
        Args:
            correct: Whether the answer was correct
            latency_ms: Time taken to answer in milliseconds
            
        Returns:
            Adjusted correctness value between 0 and 1
        """
        if correct:
            # If correct but took too long (>6s), might be guessing
            if latency_ms > 6000:
                return 0.75
            return 1.0
        else:
            # If incorrect but very fast (<1.5s), might be a slip
            if latency_ms < 1500:
                return 0.25
            return 0.0
    
    def select_next_exercise(self, exercises: List[Exercise], 
                           mastery_by_skill: Dict[str, float],
                           recent_answers: Dict[str, List[bool]]) -> Tuple[Exercise, str]:
        """
        Select the next exercise based on current mastery levels and recent performance.
        
        Args:
            exercises: Available exercises
            mastery_by_skill: Current mastery levels per skill
            recent_answers: Recent answer history per skill
            
        Returns:
            Tuple of (selected_exercise, human_readable_reason)
        """
        if not exercises:
            raise ValueError("No exercises available")
        
        # Find skill with lowest mastery
        skill_mastery = [(skill, mastery) for skill, mastery in mastery_by_skill.items()]
        skill_mastery.sort(key=lambda x: x[1])
        
        target_skill = skill_mastery[0][0]
        target_mastery = skill_mastery[0][1]
        
        # Filter exercises for target skill
        skill_exercises = [ex for ex in exercises if ex.skill == target_skill]
        
        if not skill_exercises:
            # Fallback to any exercise if no exercises for target skill
            skill_exercises = exercises
            target_skill = skill_exercises[0].skill
            target_mastery = mastery_by_skill.get(target_skill, 0.0)
        
        # Determine difficulty based on mastery level
        suggested_difficulty = self._suggest_difficulty(target_mastery, recent_answers.get(target_skill, []))
        
        # Filter by suggested difficulty
        difficulty_exercises = [ex for ex in skill_exercises if ex.difficulty == suggested_difficulty]
        
        if not difficulty_exercises:
            # Fallback to any difficulty for the skill
            difficulty_exercises = skill_exercises
        
        # Select exercise (could add more sophisticated selection here)
        selected_exercise = difficulty_exercises[0]
        
        # Generate human-readable reason
        reason = self._generate_reason(target_skill, target_mastery, suggested_difficulty, 
                                     recent_answers.get(target_skill, []))
        
        return selected_exercise, reason
    
    def _suggest_difficulty(self, mastery: float, recent_answers: List[bool]) -> Difficulty:
        """
        Suggest difficulty level based on mastery and recent performance.
        
        Args:
            mastery: Current mastery level (0-1)
            recent_answers: Recent answer history for the skill
            
        Returns:
            Suggested difficulty level
        """
        # Check if we should back off due to recent failures
        if len(recent_answers) >= 2 and not any(recent_answers[-2:]):
            # Last two were wrong, back off one difficulty tier
            if mastery > 0.7:
                return Difficulty.MEDIUM
            elif mastery > 0.35:
                return Difficulty.EASY
            else:
                return Difficulty.EASY  # Already at easiest
        
        # Normal difficulty selection based on mastery
        if mastery < 0.35:
            return Difficulty.EASY
        elif mastery < 0.7:
            return Difficulty.MEDIUM
        else:
            return Difficulty.HARD
    
    def _generate_reason(self, skill: str, mastery: float, difficulty: Difficulty, 
                        recent_answers: List[bool]) -> str:
        """
        Generate a human-readable explanation for exercise selection.
        
        Args:
            skill: Target skill
            mastery: Current mastery level
            difficulty: Selected difficulty
            recent_answers: Recent answer history
            
        Returns:
            Human-readable explanation
        """
        mastery_percent = int(mastery * 100)
        
        if len(recent_answers) >= 2 and not any(recent_answers[-2:]):
            return f"You've struggled with {skill} recently (last 2 wrong). Trying a {difficulty.value} exercise to reinforce your understanding."
        elif mastery < 0.35:
            return f"Your {skill} mastery is {mastery_percent}%. Starting with {difficulty.value} exercises to build confidence."
        elif mastery < 0.7:
            return f"Your {skill} mastery is {mastery_percent}%. Moving to {difficulty.value} exercises to challenge you appropriately."
        else:
            return f"Your {skill} mastery is {mastery_percent}%. Time for {difficulty.value} exercises to push your limits!"
