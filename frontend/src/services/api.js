import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const apiService = {
  // Health check
  async checkHealth() {
    const response = await api.get('/api/v1/health');
    return response.data;
  },

  // Chat endpoints
  async sendMessage(message, sessionId = null, enableGuardrails = true, returnTraces = false) {
    const response = await api.post('/api/v1/chat', {
      message,
      session_id: sessionId,
      enable_guardrails: enableGuardrails,
      return_traces: returnTraces,
    });
    return response.data;
  },

  async getChatHistory(sessionId, limit = 20) {
    const response = await api.get(`/api/v1/chat/sessions/${sessionId}/history`, {
      params: { limit },
    });
    return response.data;
  },

  // Traces endpoints
  async getTraces(params = {}) {
    const response = await api.get('/api/v1/traces', { params });
    return response.data;
  },

  async getTraceById(traceId) {
    const response = await api.get(`/api/v1/traces/${traceId}`);
    return response.data;
  },

  // Audit endpoints
  async getAuditLogs(params = {}) {
    const response = await api.get('/api/v1/audit', { params });
    return response.data;
  },

  async getAuditStats(startTime = null, endTime = null) {
    const response = await api.get('/api/v1/audit/stats', {
      params: { start_time: startTime, end_time: endTime },
    });
    return response.data;
  },
};

export default apiService;
