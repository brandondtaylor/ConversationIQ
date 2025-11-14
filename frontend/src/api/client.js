import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Agents API
export const agentsAPI = {
  list: (params) => apiClient.get('/agents', { params }),
  get: (id) => apiClient.get(`/agents/${id}`),
  create: (data) => apiClient.post('/agents', data),
  update: (id, data) => apiClient.put(`/agents/${id}`, data),
  delete: (id) => apiClient.delete(`/agents/${id}`),
  generate: (params) => apiClient.post('/agents/generate', null, { params }),
};

// API Configs API
export const apiConfigsAPI = {
  list: () => apiClient.get('/api-configs'),
  get: (id) => apiClient.get(`/api-configs/${id}`),
  create: (data) => apiClient.post('/api-configs', data),
  update: (id, data) => apiClient.put(`/api-configs/${id}`, data),
  delete: (id) => apiClient.delete(`/api-configs/${id}`),
  test: (id) => apiClient.post(`/api-configs/${id}/test`),
};

// Tests API
export const testsAPI = {
  list: (params) => apiClient.get('/tests', { params }),
  get: (id) => apiClient.get(`/tests/${id}`),
  create: (data) => apiClient.post('/tests', data),
  update: (id, data) => apiClient.put(`/tests/${id}`, data),
  delete: (id) => apiClient.delete(`/tests/${id}`),
  run: (id) => apiClient.post(`/tests/${id}/run`),
  getStatus: (id) => apiClient.get(`/tests/${id}/status`),
  getQuestions: (id) => apiClient.get(`/tests/${id}/questions`),
  addQuestions: (id, questions) => apiClient.post(`/tests/${id}/questions`, questions),
};

// Questions API
export const questionsAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/questions/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  parse: (text, delimiter) => apiClient.post('/questions/parse', null, {
    params: { questions_text: text, delimiter },
  }),
};

// Results API
export const resultsAPI = {
  get: (testId) => apiClient.get(`/results/${testId}`),
  getSummary: (testId) => apiClient.get(`/results/${testId}/summary`),
  getEvaluations: (testId) => apiClient.get(`/results/${testId}/evaluations`),
  getByQuestion: (testId) => apiClient.get(`/results/${testId}/by-question`),
  getByAgent: (testId) => apiClient.get(`/results/${testId}/by-agent`),
  export: (testId, format) => apiClient.get(`/results/${testId}/export`, {
    params: { format },
    responseType: 'blob',
  }),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => apiClient.get('/dashboard'),
};

// Analytics API
export const analyticsAPI = {
  // Focus Group Insights
  getFocusGroupInsights: (evaluationId) =>
    apiClient.get(`/analytics/focus-group-insights/${evaluationId}`),

  // Trend Analysis
  getTrends: (testId, params) =>
    apiClient.get(`/analytics/trends/${testId}`, { params }),

  // Agent Performance
  getAgentPerformance: (testId, agentId) =>
    apiClient.get(`/analytics/agent-performance/${testId}/${agentId}`),

  // Question Analysis
  getQuestionAnalysis: (testId, questionId) =>
    apiClient.get(`/analytics/question-analysis/${testId}/${questionId}`),

  // Comparative Analysis
  getComparativeAnalysis: (testId, params) =>
    apiClient.get(`/analytics/comparative/${testId}`, { params }),

  // Test Evaluations (for checking focus group data)
  getTestEvaluations: (testId) =>
    apiClient.get(`/results/${testId}/evaluations`),
};

export default apiClient;
