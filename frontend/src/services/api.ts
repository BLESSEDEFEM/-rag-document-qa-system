const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/documents';

// TypeScript Interfaces
interface DocumentMetadata {
  id: number;
  filename: string;
  unique_filename: string;
  file_type: string;
  file_size: number;
  status: string;
  page_count: number | null;
  upload_date: string;
  character_count: number;
  chunk_count?: number;
}

interface UploadResponse {
  message: string;
  document_id: number;
  filename: string;
  unique_filename: string;
  size_bytes: number;
  file_type: string;
  status: string;
  page_count: number | null;
  character_count: number;
  chunk_count: number | null;
  embedding_dimension: number | null;
  is_embedded: boolean;
  upload_date: string;
  extracted_text_preview: string | null;
}

interface AnswerSource {
  chunk_text: string;
  relevance_score: number;
  filename: string;
  chunk_index: number;
}

interface RetrievalStats {
  chunks_retrieved: number;
  chunks_after_filter: number;
  top_k: number;
  min_score: number;
}

interface AnswerResponse {
  success: boolean;
  answer: string;
  query: string;
  chunks_used: number;
  sources: AnswerSource[];
  retrieval_stats: RetrievalStats;
}

// Helper to get auth token from global window object
const getAuthToken = (): string | null => {
  return (window as any).clerkToken || null;
};

// API Functions with Authentication
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const token = getAuthToken();
  const headers: HeadersInit = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Upload failed');
  }

  return response.json();
};

export const getDocuments = async (): Promise<DocumentMetadata[]> => {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/list`, { headers });

  if (!response.ok) {
    throw new Error('Failed to fetch documents');
  }

  return response.json();
};

export const answerQuestion = async (
  query: string,
  top_k: number = 5,
  min_score: number = 0.3,
  document_id?: number
): Promise<AnswerResponse> => {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/answer`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ query, top_k, min_score, document_id }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to get answer');
  }

  return response.json();
};

export const deleteDocument = async (documentId: number): Promise<void> => {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/${documentId}`, {
    method: 'DELETE',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to delete document');
  }
};
