import { useState } from 'react';
import { answerQuestion } from '../services/api';

function QueryAnswer() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await answerQuestion(query.trim());
      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>💬 Ask a Question</h2>
      
      <form onSubmit={handleSubmit} style={styles.form}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your documents..."
          style={styles.textarea}
          rows={3}
        />
        
        <button
          type="submit"
          disabled={loading || !query.trim()}
          style={{
            ...styles.button,
            ...(loading || !query.trim() ? styles.buttonDisabled : {}),
          }}
        >
          {loading ? '🤔 Thinking...' : '🚀 Ask'}
        </button>
      </form>

      {error && <div style={styles.error}>{error}</div>}

      {result && (
        <div style={styles.result}>
          <h3 style={styles.resultTitle}>✨ Answer:</h3>
          <div style={styles.answer}>{result.answer}</div>
          
          {result.sources && result.sources.length > 0 && (
            <div style={styles.sources}>
              <h4 style={styles.sourcesTitle}>📚 Sources:</h4>
              {result.sources.map((source, index) => (
                <div key={index} style={styles.source}>
                  <span style={styles.sourceIcon}>📄</span>
                  <div>
                    <div style={styles.sourceName}>{source.filename}</div>
                    <div style={styles.sourceMeta}>
                      Chunk {source.chunk_index + 1} • 
                      Relevance: {(source.relevance_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {result.retrieval_stats && (
            <div style={styles.stats}>
              📊 Retrieved {result.retrieval_stats.chunks_retrieved} chunks, 
              used {result.chunks_used} for answer
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
  },
  title: {
    marginTop: 0,
    color: '#333',
  },
  form: {
    marginBottom: '20px',
  },
  textarea: {
    width: '100%',
    padding: '10px',
    fontSize: '16px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    marginBottom: '10px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  button: {
    backgroundColor: '#2196F3',
    color: 'white',
    padding: '12px 24px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  error: {
    padding: '15px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px',
    marginTop: '10px',
  },
  result: {
    marginTop: '20px',
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    border: '1px solid #ddd',
  },
  resultTitle: {
    marginTop: 0,
    color: '#1976d2',
  },
  answer: {
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#333',
    whiteSpace: 'pre-wrap',
    marginBottom: '20px',
  },
  sources: {
    marginTop: '20px',
    paddingTop: '20px',
    borderTop: '1px solid #eee',
  },
  sourcesTitle: {
    marginTop: 0,
    marginBottom: '10px',
    color: '#666',
  },
  source: {
    display: 'flex',
    alignItems: 'center',
    padding: '10px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
    marginBottom: '8px',
  },
  sourceIcon: {
    fontSize: '20px',
    marginRight: '10px',
  },
  sourceName: {
    fontWeight: 'bold',
    color: '#333',
  },
  sourceMeta: {
    fontSize: '12px',
    color: '#666',
  },
  stats: {
    fontSize: '12px',
    color: '#666',
    marginTop: '15px',
    padding: '10px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
  },
};

export default QueryAnswer;