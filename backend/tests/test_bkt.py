import pytest
import numpy as np
from bkt import BayesianKnowledgeTracing
from models import BKTParams, Exercise, Difficulty


class TestBayesianKnowledgeTracing:
    """Test cases for the Bayesian Knowledge Tracing implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bkt = BayesianKnowledgeTracing()
        self.params = BKTParams()
    
    def test_latency_adjustment_correct_slow(self):
        """Test latency adjustment for correct but slow answers."""
        # Correct answer but >6s should be treated as 0.75
        adjusted = self.bkt._adjust_for_latency(True, 7000)
        assert adjusted == 0.75
    
    def test_latency_adjustment_correct_fast(self):
        """Test latency adjustment for correct and fast answers."""
        # Correct answer and <6s should remain 1.0
        adjusted = self.bkt._adjust_for_latency(True, 2000)
        assert adjusted == 1.0
    
    def test_latency_adjustment_incorrect_fast(self):
        """Test latency adjustment for incorrect but fast answers."""
        # Incorrect answer but <1.5s should be treated as 0.25 (slip)
        adjusted = self.bkt._adjust_for_latency(False, 1000)
        assert adjusted == 0.25
    
    def test_latency_adjustment_incorrect_slow(self):
        """Test latency adjustment for incorrect and slow answers."""
        # Incorrect answer and >1.5s should remain 0.0
        adjusted = self.bkt._adjust_for_latency(False, 3000)
        assert adjusted == 0.0
    
    def test_posterior_update_correct(self):
        """Test posterior update for correct answers."""
        p_known = 0.3
        new_p = self.bkt.update_posterior(p_known, True, 2000, self.params)
        # Should increase probability of knowing
        assert new_p > p_known
        assert 0 <= new_p <= 1
    
    def test_posterior_update_incorrect(self):
        """Test posterior update for incorrect answers."""
        p_known = 0.7
        new_p = self.bkt.update_posterior(p_known, False, 3000, self.params)
        # Should decrease probability of knowing
        assert new_p < p_known
        assert 0 <= new_p <= 1
    
    def test_posterior_update_boundaries(self):
        """Test posterior update at boundary values."""
        # Test with p_known = 0
        new_p_zero = self.bkt.update_posterior(0.0, True, 2000, self.params)
        assert 0 <= new_p_zero <= 1
        
        # Test with p_known = 1
        new_p_one = self.bkt.update_posterior(1.0, False, 3000, self.params)
        assert 0 <= new_p_one <= 1
    
    def test_difficulty_suggestion_low_mastery(self):
        """Test difficulty suggestion for low mastery."""
        difficulty = self.bkt._suggest_difficulty(0.2, [])
        assert difficulty == Difficulty.EASY
    
    def test_difficulty_suggestion_medium_mastery(self):
        """Test difficulty suggestion for medium mastery."""
        difficulty = self.bkt._suggest_difficulty(0.5, [])
        assert difficulty == Difficulty.MEDIUM
    
    def test_difficulty_suggestion_high_mastery(self):
        """Test difficulty suggestion for high mastery."""
        difficulty = self.bkt._suggest_difficulty(0.8, [])
        assert difficulty == Difficulty.HARD
    
    def test_difficulty_backoff_after_failures(self):
        """Test difficulty backoff after recent failures."""
        # High mastery but last two wrong should back off to medium
        difficulty = self.bkt._suggest_difficulty(0.8, [False, False])
        assert difficulty == Difficulty.MEDIUM
        
        # Medium mastery but last two wrong should back off to easy
        difficulty = self.bkt._suggest_difficulty(0.5, [False, False])
        assert difficulty == Difficulty.EASY
    
    def test_exercise_selection_lowest_mastery(self):
        """Test that exercise selection picks skill with lowest mastery."""
        exercises = [
            Exercise(id="1", skill="A", prompt="test", choices=["a"], answer_index=0, difficulty="easy"),
            Exercise(id="2", skill="B", prompt="test", choices=["a"], answer_index=0, difficulty="easy"),
        ]
        mastery = {"A": 0.3, "B": 0.1}  # B has lower mastery
        recent_answers = {"A": [], "B": []}
        
        selected, reason = self.bkt.select_next_exercise(exercises, mastery, recent_answers)
        assert selected.skill == "B"
        assert "B" in reason
    
    def test_exercise_selection_difficulty_matching(self):
        """Test that exercise selection matches suggested difficulty."""
        exercises = [
            Exercise(id="1", skill="A", prompt="test", choices=["a"], answer_index=0, difficulty="easy"),
            Exercise(id="2", skill="A", prompt="test", choices=["a"], answer_index=0, difficulty="hard"),
        ]
        mastery = {"A": 0.2}  # Low mastery should suggest easy
        recent_answers = {"A": []}
        
        selected, reason = self.bkt.select_next_exercise(exercises, mastery, recent_answers)
        assert selected.difficulty == Difficulty.EASY
    
    def test_reason_generation(self):
        """Test human-readable reason generation."""
        # Test low mastery reason
        reason = self.bkt._generate_reason("TestSkill", 0.2, Difficulty.EASY, [])
        assert "TestSkill" in reason
        assert "20%" in reason
        assert "easy" in reason
        
        # Test recent failures reason
        reason = self.bkt._generate_reason("TestSkill", 0.8, Difficulty.MEDIUM, [False, False])
        assert "struggled" in reason.lower()
        assert "TestSkill" in reason
    
    def test_exercise_selection_empty_list(self):
        """Test error handling for empty exercise list."""
        with pytest.raises(ValueError, match="No exercises available"):
            self.bkt.select_next_exercise([], {}, {})
    
    def test_posterior_update_with_latency_adjustment(self):
        """Test that latency adjustments affect posterior updates."""
        p_known = 0.5
        
        # Fast correct answer
        fast_correct = self.bkt.update_posterior(p_known, True, 1000, self.params)
        
        # Slow correct answer (should be treated as 0.75)
        slow_correct = self.bkt.update_posterior(p_known, True, 7000, self.params)
        
        # Fast correct should increase more than slow correct
        assert fast_correct > slow_correct
        
        # Fast incorrect answer (should be treated as 0.25)
        fast_incorrect = self.bkt.update_posterior(p_known, False, 1000, self.params)
        
        # Slow incorrect answer
        slow_incorrect = self.bkt.update_posterior(p_known, False, 3000, self.params)
        
        # Fast incorrect should decrease less than slow incorrect
        assert fast_incorrect > slow_incorrect
