import axios from 'axios';

// Base URL for backend API
const API_BASE_URL = 'http://localhost:8000/api/documents';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload document
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Get all documents
export const getDocuments = async () => {
  const response = await api.get('/list');
  return response.data;
};

// Query documents (retrieval only)
export const queryDocuments = async (query, topK = 5, minScore = 0.3) => {
  const response = await api.post('/query', null, {
    params: { query, top_k: topK, min_score: minScore },
  });
  return response.data;
};

// Answer question (complete RAG)
export const answerQuestion = async (query, topK = 5, minScore = 0.3) => {
  const response = await api.post('/answer', null, {
    params: { query, top_k: topK, min_score: minScore },
  });
  return response.data;
};

export default api;