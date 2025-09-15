from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Exercise(BaseModel):
    id: str
    skill: str
    prompt: str
    choices: List[str]
    answer_index: int
    difficulty: Difficulty


class AnswerRequest(BaseModel):
    exercise_id: str
    correct: bool
    latency_ms: int


class NextExerciseRequest(BaseModel):
    exclude_ids: Optional[List[str]] = None


class MasteryResponse(BaseModel):
    updated_mastery: Dict[str, float]


class NextExerciseResponse(BaseModel):
    exercise: Exercise
    reason: str
    mastery: Dict[str, float]


class HealthResponse(BaseModel):
    ok: bool


class BKTParams(BaseModel):
    l0: float = 0.2  # Prior probability of knowing
    t: float = 0.15  # Learning rate
    s: float = 0.1   # Slip rate
    g: float = 0.2   # Guess rate


class SessionState(BaseModel):
    mastery: Dict[str, float]  # skill -> p(known)
    recent_answers: Dict[str, List[bool]]  # skill -> recent correctness
    bkt_params: Dict[str, BKTParams]  # skill -> BKT parameters
