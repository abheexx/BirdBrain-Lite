from typing import Dict, List
from models import Exercise, SessionState, BKTParams
import json
import os


class InMemoryStore:
    """In-memory store for session state and exercises."""
    
    def __init__(self):
        self.session_state = self._initialize_session()
        self.exercises = self._load_exercises()
    
    def _initialize_session(self) -> SessionState:
        """Initialize a fresh session state."""
        skills = ["Basics", "Plurals", "IrregularVerbs"]
        mastery = {skill: 0.2 for skill in skills}  # Start with L0 prior
        recent_answers = {skill: [] for skill in skills}
        bkt_params = {skill: BKTParams() for skill in skills}
        
        return SessionState(
            mastery=mastery,
            recent_answers=recent_answers,
            bkt_params=bkt_params
        )
    
    def _load_exercises(self) -> List[Exercise]:
        """Load exercises from JSON file."""
        data_dir = os.path.dirname(__file__)
        exercises_file = os.path.join(data_dir, "data", "exercises.json")
        
        try:
            with open(exercises_file, 'r') as f:
                data = json.load(f)
                return [Exercise(**exercise) for exercise in data]
        except FileNotFoundError:
            # Return default exercises if file doesn't exist
            return self._get_default_exercises()
    
    def _get_default_exercises(self) -> List[Exercise]:
        """Return default exercises if JSON file is not available."""
        return [
            Exercise(
                id="basics_1",
                skill="Basics",
                prompt="What is the correct form of 'I am'?",
                choices=["I am", "I is", "I are", "I be"],
                answer_index=0,
                difficulty="easy"
            ),
            Exercise(
                id="basics_2",
                skill="Basics",
                prompt="Choose the correct verb: 'She ___ happy.'",
                choices=["is", "are", "am", "be"],
                answer_index=0,
                difficulty="easy"
            ),
            Exercise(
                id="basics_3",
                skill="Basics",
                prompt="What is the past tense of 'go'?",
                choices=["goed", "went", "gone", "goes"],
                answer_index=1,
                difficulty="medium"
            ),
            Exercise(
                id="plurals_1",
                skill="Plurals",
                prompt="What is the plural of 'child'?",
                choices=["childs", "children", "childes", "child"],
                answer_index=1,
                difficulty="easy"
            ),
            Exercise(
                id="plurals_2",
                skill="Plurals",
                prompt="What is the plural of 'mouse'?",
                choices=["mouses", "mice", "mouse", "mousies"],
                answer_index=1,
                difficulty="medium"
            ),
            Exercise(
                id="plurals_3",
                skill="Plurals",
                prompt="What is the plural of 'cactus'?",
                choices=["cactuses", "cacti", "cactus", "cactuses or cacti"],
                answer_index=3,
                difficulty="hard"
            ),
            Exercise(
                id="irregular_1",
                skill="IrregularVerbs",
                prompt="What is the past tense of 'swim'?",
                choices=["swimmed", "swam", "swum", "swim"],
                answer_index=1,
                difficulty="easy"
            ),
            Exercise(
                id="irregular_2",
                skill="IrregularVerbs",
                prompt="What is the past participle of 'break'?",
                choices=["breaked", "broke", "broken", "break"],
                answer_index=2,
                difficulty="medium"
            ),
            Exercise(
                id="irregular_3",
                skill="IrregularVerbs",
                prompt="What is the past tense of 'lie' (to recline)?",
                choices=["lied", "lay", "lain", "lie"],
                answer_index=1,
                difficulty="hard"
            )
        ]
    
    def reset_session(self) -> None:
        """Reset the session state to initial values."""
        self.session_state = self._initialize_session()
    
    def get_exercises(self) -> List[Exercise]:
        """Get all available exercises."""
        return self.exercises
    
    def get_exercise_by_id(self, exercise_id: str) -> Exercise:
        """Get a specific exercise by ID."""
        for exercise in self.exercises:
            if exercise.id == exercise_id:
                return exercise
        raise ValueError(f"Exercise with ID {exercise_id} not found")
    
    def update_mastery(self, skill: str, new_mastery: float) -> None:
        """Update mastery level for a skill."""
        self.session_state.mastery[skill] = new_mastery
    
    def add_recent_answer(self, skill: str, correct: bool) -> None:
        """Add a recent answer to the skill's history."""
        self.session_state.recent_answers[skill].append(correct)
        # Keep only last 5 answers to prevent memory growth
        if len(self.session_state.recent_answers[skill]) > 5:
            self.session_state.recent_answers[skill] = self.session_state.recent_answers[skill][-5:]
    
    def get_mastery(self) -> Dict[str, float]:
        """Get current mastery levels for all skills."""
        return self.session_state.mastery.copy()
    
    def get_recent_answers(self) -> Dict[str, List[bool]]:
        """Get recent answer history for all skills."""
        return {skill: answers.copy() for skill, answers in self.session_state.recent_answers.items()}
    
    def get_bkt_params(self) -> Dict[str, BKTParams]:
        """Get BKT parameters for all skills."""
        return self.session_state.bkt_params.copy()
