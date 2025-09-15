const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status
      );
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(`Network error: ${error.message}`, 0);
  }
}

export const api = {
  // Health check
  async healthCheck() {
    return apiRequest('/health');
  },

  // Session management
  async resetSession() {
    return apiRequest('/session/reset', { method: 'POST' });
  },

  // Exercises
  async getExercises() {
    return apiRequest('/exercises');
  },

  // Learning
  async submitAnswer(exerciseId, correct, latencyMs) {
    return apiRequest('/answer', {
      method: 'POST',
      body: JSON.stringify({
        exercise_id: exerciseId,
        correct,
        latency_ms: latencyMs,
      }),
    });
  },

  async getNextExercise(excludeIds = []) {
    return apiRequest('/next', {
      method: 'POST',
      body: JSON.stringify({
        exclude_ids: excludeIds,
      }),
    });
  },
};

export { APIError };
