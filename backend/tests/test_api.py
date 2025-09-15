import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


def test_reset_session():
    """Test session reset endpoint."""
    response = client.post("/session/reset")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_get_exercises():
    """Test getting all exercises."""
    response = client.get("/exercises")
    assert response.status_code == 200
    exercises = response.json()
    assert isinstance(exercises, list)
    assert len(exercises) > 0
    
    # Check structure of first exercise
    exercise = exercises[0]
    required_fields = ["id", "skill", "prompt", "choices", "answer_index", "difficulty"]
    for field in required_fields:
        assert field in exercise


def test_submit_answer():
    """Test submitting an answer."""
    # First get an exercise
    exercises_response = client.get("/exercises")
    exercises = exercises_response.json()
    exercise = exercises[0]
    
    # Submit correct answer
    answer_data = {
        "exercise_id": exercise["id"],
        "correct": True,
        "latency_ms": 2000
    }
    
    response = client.post("/answer", json=answer_data)
    assert response.status_code == 200
    data = response.json()
    assert "updated_mastery" in data
    assert isinstance(data["updated_mastery"], dict)


def test_submit_answer_invalid_exercise():
    """Test submitting answer with invalid exercise ID."""
    answer_data = {
        "exercise_id": "nonexistent",
        "correct": True,
        "latency_ms": 2000
    }
    
    response = client.post("/answer", json=answer_data)
    assert response.status_code == 404


def test_get_next_exercise():
    """Test getting next exercise."""
    response = client.post("/next", json={})
    assert response.status_code == 200
    data = response.json()
    
    required_fields = ["exercise", "reason", "mastery"]
    for field in required_fields:
        assert field in data
    
    # Check exercise structure
    exercise = data["exercise"]
    exercise_fields = ["id", "skill", "prompt", "choices", "answer_index", "difficulty"]
    for field in exercise_fields:
        assert field in exercise


def test_get_next_exercise_with_exclusions():
    """Test getting next exercise with exclusions."""
    # First get all exercises
    exercises_response = client.get("/exercises")
    exercises = exercises_response.json()
    
    # Exclude first exercise
    exclude_ids = [exercises[0]["id"]]
    
    response = client.post("/next", json={"exclude_ids": exclude_ids})
    assert response.status_code == 200
    data = response.json()
    
    # Check that excluded exercise is not returned
    assert data["exercise"]["id"] != exclude_ids[0]


def test_answer_affects_next_exercise():
    """Test that answering affects the next exercise selection."""
    # Get initial next exercise
    response1 = client.post("/next", json={})
    assert response1.status_code == 200
    initial_exercise = response1.json()["exercise"]
    
    # Submit a wrong answer
    answer_data = {
        "exercise_id": initial_exercise["id"],
        "correct": False,
        "latency_ms": 5000
    }
    client.post("/answer", json=answer_data)
    
    # Get next exercise - should potentially be different
    response2 = client.post("/next", json={})
    assert response2.status_code == 200
    next_exercise = response2.json()["exercise"]
    
    # The exercise might be the same or different, but the mastery should be updated
    mastery1 = response1.json()["mastery"]
    mastery2 = response2.json()["mastery"]
    
    # Mastery levels should be different after the answer
    assert mastery1 != mastery2


def test_latency_affects_mastery():
    """Test that different latencies affect mastery differently."""
    # Get an exercise
    exercises_response = client.get("/exercises")
    exercises = exercises_response.json()
    exercise = exercises[0]
    
    # Submit correct answer with fast latency
    fast_answer = {
        "exercise_id": exercise["id"],
        "correct": True,
        "latency_ms": 1000
    }
    fast_response = client.post("/answer", json=fast_answer)
    fast_mastery = fast_response.json()["updated_mastery"]
    
    # Reset session
    client.post("/session/reset")
    
    # Submit correct answer with slow latency
    slow_answer = {
        "exercise_id": exercise["id"],
        "correct": True,
        "latency_ms": 7000
    }
    slow_response = client.post("/answer", json=slow_answer)
    slow_mastery = slow_response.json()["updated_mastery"]
    
    # Fast correct should increase mastery more than slow correct
    skill = exercise["skill"]
    assert fast_mastery[skill] > slow_mastery[skill]
