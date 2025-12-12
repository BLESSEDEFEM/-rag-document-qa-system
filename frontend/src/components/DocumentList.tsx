import { useState, useEffect } from 'react';
import { getDocuments } from '../services/api';

interface DocumentListProps {
  refreshTrigger: number;
}

interface Document {
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

function DocumentList({ refreshTrigger }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);

    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load documents';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getFileIcon = (fileType: string): string => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return '📕';
      case 'docx':
      case 'doc':
        return '📘';
      case 'txt':
        return '📄';
      default:
        return '📄';
    }
  };

  if (loading && documents.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-3 rounded-lg">
            <span className="text-2xl">📚</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-800">Uploaded Documents</h2>
        </div>
        <div className="flex flex-col items-center justify-center py-12">
          <svg className="animate-spin h-12 w-12 text-primary-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-slate-500">Loading documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-slate-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-3 rounded-lg">
            <span className="text-2xl">📚</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Uploaded Documents</h2>
            <p className="text-sm text-slate-500">{documents.length} document{documents.length !== 1 ? 's' : ''}</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg animate-fade-in">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <p className="text-sm text-red-700 font-medium">{error}</p>
          </div>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="text-center py-12 px-4">
          <div className="inline-block p-4 bg-slate-100 rounded-full mb-4">
            <span className="text-4xl">📂</span>
          </div>
          <p className="text-slate-500 text-lg">No documents uploaded yet</p>
          <p className="text-slate-400 text-sm mt-2">Upload your first document to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc, index) => (
            <div
              key={doc.id}
              className="group p-4 bg-gradient-to-r from-slate-50 to-slate-100 hover:from-primary-50 hover:to-blue-50 rounded-lg border border-slate-200 hover:border-primary-300 transition-all duration-200 animate-fade-in"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 text-3xl">
                  {getFileIcon(doc.file_type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h3 className="text-base font-semibold text-slate-800 truncate group-hover:text-primary-700 transition-colors">
                      {doc.filename}
                    </h3>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {doc.status === 'ready' ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          ✅ Ready
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          ⏳ Processing
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      📦 {formatFileSize(doc.file_size)}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      🕒 {formatDate(doc.upload_date)}
                    </span>
                    {doc.chunk_count && (
                      <>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          📑 {doc.chunk_count} chunks
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentList;
