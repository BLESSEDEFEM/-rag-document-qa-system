import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import QueryAnswer from './components/QueryAnswer';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-2 flex items-center gap-2">
            🤖 RAG Document Q&A System
          </h1>
          <p className="text-primary-100 text-sm sm:text-base">
            Upload documents and ask questions powered by AI
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Upload Section */}
        <div className="animate-fade-in">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Documents List */}
        <div className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <DocumentList refreshTrigger={refreshTrigger} />
        </div>

        {/* Query Section */}
        <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <QueryAnswer />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-slate-600 text-sm">
            Built with <span className="text-red-500">♥</span> using FastAPI + React + TypeScript + Pinecone + Gemini AI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;