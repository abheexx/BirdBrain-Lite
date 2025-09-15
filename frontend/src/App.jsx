import React, { useState, useEffect, useCallback } from 'react';
import { api, APIError } from './api';

function MasteryBar({ skill, mastery, streak }) {
  const percentage = Math.round(mastery * 100);
  const getColorClass = (percentage) => {
    if (percentage < 30) return 'bg-danger-500';
    if (percentage < 60) return 'bg-warning-500';
    if (percentage < 80) return 'bg-duolingo-500';
    return 'bg-duolingo-600';
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">{skill}</span>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">{percentage}%</span>
          {streak > 0 && (
            <span className="text-xs bg-success-100 text-success-800 px-2 py-1 rounded-full">
              {streak} streak
            </span>
          )}
        </div>
      </div>
      <div className="mastery-bar">
        <div
          className={`mastery-fill ${getColorClass(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function ExerciseCard({ exercise, onSubmit, isSubmitting }) {
  const [selectedChoice, setSelectedChoice] = useState(null);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    if (exercise) {
      setSelectedChoice(null);
      setStartTime(performance.now());
    }
  }, [exercise]);

  const handleSubmit = () => {
    if (selectedChoice === null) return;
    
    const endTime = performance.now();
    const latency = Math.round(endTime - startTime);
    const correct = selectedChoice === exercise.answer_index;
    
    onSubmit(exercise.id, correct, latency);
  };

  if (!exercise) {
    return (
      <div className="card text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Ready to learn?</h3>
        <p className="text-gray-600">Click "Get Next Exercise" to start!</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-duolingo-100 text-duolingo-800">
            {exercise.skill}
          </span>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {exercise.difficulty}
          </span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {exercise.prompt}
        </h3>
      </div>

      <div className="space-y-3 mb-6">
        {exercise.choices.map((choice, index) => (
          <label
            key={index}
            className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
              selectedChoice === index
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name="choice"
              value={index}
              checked={selectedChoice === index}
              onChange={() => setSelectedChoice(index)}
              className="sr-only"
            />
            <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
              selectedChoice === index
                ? 'border-primary-500 bg-primary-500'
                : 'border-gray-300'
            }`}>
              {selectedChoice === index && (
                <div className="w-2 h-2 bg-white rounded-full" />
              )}
            </div>
            <span className="text-gray-900">{choice}</span>
          </label>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={selectedChoice === null || isSubmitting}
        className="btn-primary w-full"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Answer'}
      </button>
    </div>
  );
}

function App() {
  const [mastery, setMastery] = useState({});
  const [currentExercise, setCurrentExercise] = useState(null);
  const [reason, setReason] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [streaks, setStreaks] = useState({});
  const [lastLatency, setLastLatency] = useState(null);

  const loadMastery = useCallback(async () => {
    try {
      const response = await api.getNextExercise();
      setMastery(response.mastery);
    } catch (err) {
      console.error('Failed to load mastery:', err);
    }
  }, []);

  const getNextExercise = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await api.getNextExercise();
      setCurrentExercise(response.exercise);
      setReason(response.reason);
      setMastery(response.mastery);
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Failed to load exercise');
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async (exerciseId, correct, latency) => {
    setIsSubmitting(true);
    setError('');
    setLastLatency(latency);
    
    try {
      const response = await api.submitAnswer(exerciseId, correct, latency);
      setMastery(response.updated_mastery);
      
      // Update streaks
      const skill = currentExercise.skill;
      setStreaks(prev => ({
        ...prev,
        [skill]: correct ? (prev[skill] || 0) + 1 : 0
      }));
      
      // Clear current exercise and show loading
      setCurrentExercise(null);
      setReason('');
      
      // Get next exercise after a short delay
      setTimeout(async () => {
        try {
          const nextResponse = await api.getNextExercise();
          setCurrentExercise(nextResponse.exercise);
          setReason(nextResponse.reason);
          setMastery(nextResponse.mastery);
        } catch (err) {
          setError(err instanceof APIError ? err.message : 'Failed to load next exercise');
        }
      }, 1500);
      
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Failed to submit answer');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetSession = async () => {
    try {
      await api.resetSession();
      setMastery({});
      setCurrentExercise(null);
      setReason('');
      setStreaks({});
      setLastLatency(null);
      setError('');
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Failed to reset session');
    }
  };

  useEffect(() => {
    loadMastery();
  }, [loadMastery]);

  const skills = Object.keys(mastery);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">BirdBrain Lite</h1>
          <p className="text-gray-600">Adaptive learning with Bayesian Knowledge Tracing</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Mastery Tracking */}
          <div className="lg:col-span-1">
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Mastery Progress</h2>
              
              {skills.length > 0 ? (
                <div className="space-y-6">
                  {skills.map(skill => (
                    <MasteryBar
                      key={skill}
                      skill={skill}
                      mastery={mastery[skill]}
                      streak={streaks[skill] || 0}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No data yet. Start an exercise!</p>
              )}

              {lastLatency && (
                <div className="mt-6 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Last response time: <span className="font-medium">{lastLatency}ms</span>
                  </p>
                </div>
              )}

              <button
                onClick={resetSession}
                className="btn-secondary w-full mt-6"
              >
                Reset Session
              </button>
            </div>
          </div>

          {/* Center Panel - Exercise */}
          <div className="lg:col-span-2">
            {error && (
              <div className="mb-4 p-4 bg-danger-50 border border-danger-200 rounded-lg">
                <p className="text-sm text-danger-800">{error}</p>
              </div>
            )}

            {reason && (
              <div className="mb-4 p-4 bg-duolingo-50 border border-duolingo-200 rounded-lg">
                <p className="text-sm text-duolingo-800">
                  <span className="font-medium">Why this exercise?</span> {reason}
                </p>
              </div>
            )}

            <ExerciseCard
              exercise={currentExercise}
              onSubmit={submitAnswer}
              isSubmitting={isSubmitting}
            />

            {!currentExercise && !isLoading && !isSubmitting && (
              <div className="text-center mt-6">
                <button
                  onClick={getNextExercise}
                  disabled={isLoading}
                  className="btn-primary text-lg px-8 py-3"
                >
                  {isLoading ? 'Loading...' : 'Get Next Exercise'}
                </button>
              </div>
            )}

            {!currentExercise && isSubmitting && (
              <div className="card text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-duolingo-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Processing your answer...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
