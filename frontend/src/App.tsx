import { useState } from 'react';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2 flex items-center gap-2">
                🤖 RAG Document Q&A System
              </h1>
              <p className="text-primary-100 text-xs sm:text-sm lg:text-base">
                Upload documents and ask questions powered by AI
              </p>
            </div>
            {/* Auth Buttons */}
            <div>
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="bg-white text-primary-600 px-4 py-2 rounded-lg font-semibold hover:bg-primary-50 transition-colors">
                    Sign In
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 space-y-4 sm:space-y-6">
        <SignedOut>
          {/* Landing Page for Non-Authenticated Users */}
          <div className="text-center py-20">
            <div className="inline-block p-6 bg-white rounded-full shadow-lg mb-6">
              <span className="text-6xl">🔒</span>
            </div>
            <h2 className="text-3xl font-bold text-slate-800 mb-4">
              Sign in to access your documents
            </h2>
            <p className="text-slate-600 mb-8 max-w-md mx-auto">
              Create an account or sign in to upload documents and ask questions using AI
            </p>
            <SignInButton mode="modal">
              <button className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-md">
                Get Started
              </button>
            </SignInButton>
          </div>
        </SignedOut>

        <SignedIn>
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
        </SignedIn>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-8 sm:mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <p className="text-center text-slate-600 text-xs sm:text-sm">
            Built with <span className="text-red-500">♥</span> using FastAPI + React + TypeScript + Pinecone + Gemini AI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;