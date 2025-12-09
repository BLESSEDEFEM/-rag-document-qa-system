import { useState, useEffect } from 'react';
import { getDocuments } from '../services/api';

function DocumentList({ refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);

    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return <div style={styles.container}>⏳ Loading documents...</div>;
  }

  if (error) {
    return <div style={styles.error}>{error}</div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📚 Uploaded Documents ({documents.length})</h2>
      
      {documents.length === 0 ? (
        <p style={styles.emptyState}>No documents uploaded yet.</p>
      ) : (
        <div style={styles.list}>
          {documents.map((doc) => (
            <div key={doc.id} style={styles.docCard}>
              <div style={styles.docHeader}>
                <span style={styles.docIcon}>
                  {doc.file_type === 'pdf' ? '📕' : doc.file_type === 'docx' ? '📘' : '📄'}
                </span>
                <div style={styles.docInfo}>
                  <div style={styles.docName}>{doc.filename}</div>
                  <div style={styles.docMeta}>
                    {formatBytes(doc.file_size)} • {formatDate(doc.upload_date)}
                  </div>
                </div>
              </div>
              
              <div style={styles.docStats}>
                <span style={styles.badge}>
                  {doc.status === 'ready' ? '✅' : '⏳'} {doc.status}
                </span>
                {doc.chunk_count && (
                  <span style={styles.badge}>
                    📦 {doc.chunk_count} chunks
                  </span>
                )}
              </div>
            </div>
          ))}
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
    marginBottom: '20px',
  },
  title: {
    marginTop: 0,
    color: '#333',
  },
  emptyState: {
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
    padding: '20px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  docCard: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #ddd',
  },
  docHeader: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '10px',
  },
  docIcon: {
    fontSize: '24px',
    marginRight: '10px',
  },
  docInfo: {
    flex: 1,
  },
  docName: {
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '5px',
  },
  docMeta: {
    fontSize: '12px',
    color: '#666',
  },
  docStats: {
    display: 'flex',
    gap: '10px',
  },
  badge: {
    fontSize: '12px',
    padding: '4px 8px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    color: '#1976d2',
  },
  error: {
    padding: '20px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '8px',
  },
};

export default DocumentList;