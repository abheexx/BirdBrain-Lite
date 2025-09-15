from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from models import (
    HealthResponse, AnswerRequest, MasteryResponse, 
    NextExerciseRequest, NextExerciseResponse, Exercise
)
from store import InMemoryStore
from bkt import BayesianKnowledgeTracing

# Initialize FastAPI app
app = FastAPI(
    title="BirdBrain Lite API",
    description="A Duolingo-style exercise picker with Bayesian Knowledge Tracing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store and BKT
store = InMemoryStore()
bkt = BayesianKnowledgeTracing()


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(ok=True)


@app.post("/session/reset", tags=["session"])
async def reset_session():
    """Reset the learning session to initial state."""
    store.reset_session()
    return {"message": "Session reset successfully"}


@app.get("/exercises", response_model=List[Exercise], tags=["exercises"])
async def get_exercises():
    """Get all available exercises (for debugging)."""
    return store.get_exercises()


@app.post("/answer", response_model=MasteryResponse, tags=["learning"])
async def submit_answer(request: AnswerRequest):
    """
    Submit an answer and update mastery levels using BKT.
    
    Args:
        request: Answer data including exercise ID, correctness, and latency
        
    Returns:
        Updated mastery levels for all skills
    """
    try:
        # Get the exercise to find the skill
        exercise = store.get_exercise_by_id(request.exercise_id)
        skill = exercise.skill
        
        # Get current mastery and BKT params for the skill
        current_mastery = store.get_mastery()
        bkt_params = store.get_bkt_params()[skill]
        
        # Update mastery using BKT
        new_mastery = bkt.update_posterior(
            current_mastery[skill],
            request.correct,
            request.latency_ms,
            bkt_params
        )
        
        # Update store
        store.update_mastery(skill, new_mastery)
        store.add_recent_answer(skill, request.correct)
        
        # Return updated mastery levels
        return MasteryResponse(updated_mastery=store.get_mastery())
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/next", response_model=NextExerciseResponse, tags=["learning"])
async def get_next_exercise(request: NextExerciseRequest):
    """
    Get the next exercise based on current mastery levels.
    
    Args:
        request: Optional list of exercise IDs to exclude
        
    Returns:
        Next exercise with selection reason and current mastery levels
    """
    try:
        # Get available exercises (excluding any specified)
        all_exercises = store.get_exercises()
        if request.exclude_ids:
            available_exercises = [
                ex for ex in all_exercises 
                if ex.id not in request.exclude_ids
            ]
        else:
            available_exercises = all_exercises
        
        if not available_exercises:
            raise HTTPException(status_code=404, detail="No exercises available")
        
        # Get current state
        mastery = store.get_mastery()
        recent_answers = store.get_recent_answers()
        
        # Select next exercise using BKT
        selected_exercise, reason = bkt.select_next_exercise(
            available_exercises, mastery, recent_answers
        )
        
        return NextExerciseResponse(
            exercise=selected_exercise,
            reason=reason,
            mastery=mastery
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
