import { useState, useEffect } from 'react';
import { answerQuestion, getDocuments } from '../services/api';

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

interface AnswerResult {
  success: boolean;
  answer: string;
  query: string;
  chunks_used: number;
  sources: AnswerSource[];
  retrieval_stats: RetrievalStats;
}

interface ChatMessage {
  id: string;
  type: 'question' | 'answer';
  content: string;
  sources?: AnswerSource[];
  timestamp: Date;
}

interface Document {
  id: number;
  filename: string;
}

function QueryAnswer() {
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  
  // Document filter
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [showDocFilter, setShowDocFilter] = useState(false);

  // Load documents
  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const docs = await getDocuments();
        setDocuments(docs);
      } catch (err) {
        console.error('Failed to load documents:', err);
      }
    };
    loadDocuments();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    // Add question to history
    const questionMsg: ChatMessage = {
      id: Date.now().toString(),
      type: 'question',
      content: selectedDocId 
        ? `${query} (searching in: ${documents.find(d => d.id === selectedDocId)?.filename})`
        : query,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, questionMsg]);

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Pass document filter if selected
      const response = await answerQuestion(
        query.trim(), 
        5, 
        0.3,
        selectedDocId || undefined
      );
      
      // Add answer to history
      const answerMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'answer',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, answerMsg]);
      
      setResult(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get answer';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-slate-200">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-3 rounded-lg">
          <span className="text-2xl">💬</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-800">Ask a Question</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Document Filter Toggle */}
        {documents.length > 0 && (
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-sm text-slate-600">Search specific document?</span>
            <button
              type="button"
              onClick={() => setShowDocFilter(!showDocFilter)}
              className="text-sm text-primary-600 hover:text-primary-800 font-medium"
            >
              {showDocFilter ? 'Hide filters' : 'Show filters'}
            </button>
          </div>
        )}

        {/* Document Selector */}
        {showDocFilter && documents.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Filter by document (optional)
            </label>
            <select
              value={selectedDocId || ''}
              onChange={(e) => setSelectedDocId(e.target.value ? Number(e.target.value) : null)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-slate-700"
            >
              <option value="">All documents</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  📄 {doc.filename}
                </option>
              ))}
            </select>
            {selectedDocId && (
              <p className="text-xs text-slate-500">
                ✓ Searching only in: {documents.find(d => d.id === selectedDocId)?.filename}
              </p>
            )}
          </div>
        )}

        <div>
          <textarea
            value={query}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
            placeholder="Ask a question about your documents..."
            rows={4}
            disabled={loading}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-y disabled:bg-slate-100 disabled:cursor-not-allowed transition-all text-slate-700 placeholder-slate-400"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full py-3 px-6 rounded-lg font-semibold text-white bg-gradient-to-r from-primary-500 to-blue-600 hover:from-primary-600 hover:to-blue-700 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Thinking...</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>Ask Question</span>
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg animate-fade-in">
          <div className="flex items-start gap-3">
            <span className="text-xl flex-shrink-0">⚠️</span>
            <p className="text-sm text-red-700 font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* Chat History */}
      {chatHistory.length > 0 && (
        <div className="mt-6 space-y-4 max-h-96 overflow-y-auto">
          {chatHistory.map((msg) => (
            <div
              key={msg.id}
              className={`p-4 rounded-lg transition-all ${
                msg.type === 'question'
                  ? 'bg-blue-50 border-l-4 border-blue-500 ml-8'
                  : 'bg-green-50 border-l-4 border-green-500 mr-8'
              }`}
            >
              <div className="flex items-start gap-2">
                <span className="text-xl flex-shrink-0">
                  {msg.type === 'question' ? '❓' : '✨'}
                </span>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-slate-600 mb-1">
                    {msg.type === 'question' ? 'Question' : 'Answer'}
                  </p>
                  <p className="text-slate-800 whitespace-pre-wrap">{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 text-xs text-slate-500">
                      📚 {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Clear History Button */}
      {chatHistory.length > 0 && (
        <button
          onClick={() => setChatHistory([])}
          className="mt-4 text-sm text-red-600 hover:text-red-800 hover:underline"
        >
          🗑️ Clear conversation history
        </button>
      )}

      {result && (
        <div className="mt-6 space-y-6 animate-slide-up">
          {/* Sources */}
          {result.sources && result.sources.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
                <span>📚</span>
                <span>Sources</span>
              </h4>
              <div className="space-y-3">
                {result.sources.map((source, index) => (
                  <div
                    key={index}
                    className="p-4 bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors animate-fade-in"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl flex-shrink-0">📄</span>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-800 mb-1 truncate">
                          {source.filename}
                        </p>
                        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
                          <span className="inline-flex items-center px-2 py-1 bg-white rounded border border-slate-200">
                            📑 Chunk {source.chunk_index + 1}
                          </span>
                          <span className="inline-flex items-center px-2 py-1 bg-white rounded border border-slate-200">
                            🎯 {(source.relevance_score * 100).toFixed(1)}% relevant
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          {result.retrieval_stats && (
            <div className="p-4 bg-slate-100 rounded-lg border border-slate-200">
              <p className="text-sm text-slate-600">
                📊 Retrieved <span className="font-semibold text-slate-800">{result.retrieval_stats.chunks_retrieved}</span> chunks,
                used <span className="font-semibold text-slate-800">{result.chunks_used}</span> for answer
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QueryAnswer;