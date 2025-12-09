import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import QueryAnswer from './components/QueryAnswer';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger document list refresh
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>🤖 RAG Document Q&A System</h1>
        <p style={styles.headerSubtitle}>
          Upload documents and ask questions powered by AI
        </p>
      </header>

      <div style={styles.container}>
        <div style={styles.section}>
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        <div style={styles.section}>
          <DocumentList refreshTrigger={refreshTrigger} />
        </div>

        <div style={styles.section}>
          <QueryAnswer />
        </div>
      </div>

      <footer style={styles.footer}>
        <p>Built with FastAPI + React + Pinecone + Gemini AI</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#e0e0e0',
  },
  header: {
    backgroundColor: '#1976d2',
    color: 'white',
    padding: '30px 20px',
    textAlign: 'center',
  },
  headerTitle: {
    margin: '0 0 10px 0',
    fontSize: '32px',
  },
  headerSubtitle: {
    margin: 0,
    fontSize: '16px',
    opacity: 0.9,
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
  },
  section: {
    marginBottom: '20px',
  },
  footer: {
    textAlign: 'center',
    padding: '20px',
    color: '#666',
    fontSize: '14px',
  },
};

export default App;