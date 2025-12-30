import { useState, useEffect } from 'react';
import { ClerkProvider, SignInButton, SignedIn, SignedOut, UserButton, useAuth } from '@clerk/clerk-react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import QueryAnswer from './components/QueryAnswer';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Upload, MessageSquare, LogIn } from 'lucide-react';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing Clerk Publishable Key');
}

// Component to handle token management
function TokenManager() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  
  useEffect(() => {
    const updateToken = async () => {
      if (isLoaded && isSignedIn) {
        try {
          const token = await getToken();
          if (token) {
            (window as any).clerkToken = token;
            console.log('Token set successfully');
          }
        } catch (error) {
          console.error('Failed to get token:', error);
        }
      } else if (isLoaded && !isSignedIn) {
        // Clear token when signed out
        (window as any).clerkToken = null;
      }
    };
    
    updateToken();
    
    // Refresh token periodically (every 50 minutes)
    const interval = setInterval(updateToken, 50 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [getToken, isLoaded, isSignedIn]);
  
  return null;
}

function App() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleDocumentUploaded = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleDocumentDeleted = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <TokenManager />
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-6">
          {/* Simple Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-slate-800 mb-2">
              RAG Document Q&A System
            </h1>
            <p className="text-slate-600">Upload, manage, and query your documents with AI</p>
          </div>

          {/* Auth Section */}
          <div className="mb-8 flex justify-center">
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm px-6 py-4 border border-slate-200">
              <SignedOut>
                <div className="flex items-center gap-4">
                  <LogIn className="h-5 w-5 text-slate-600" />
                  <SignInButton mode="modal">
                    <button className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-sm hover:shadow-md">
                      Sign In to Continue
                    </button>
                  </SignInButton>
                </div>
              </SignedOut>
              <SignedIn>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-slate-600">Welcome back!</span>
                  <UserButton afterSignOutUrl="/" />
                </div>
              </SignedIn>
            </div>
          </div>

          {/* Main Content */}
          <SignedIn>
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200">
              <Tabs defaultValue="upload" className="w-full">
                <TabsList className="grid w-full grid-cols-3 bg-slate-100/50">
                  <TabsTrigger value="upload" className="flex items-center gap-2">
                    <Upload className="h-4 w-4" />
                    Upload
                  </TabsTrigger>
                  <TabsTrigger value="documents" className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Documents
                  </TabsTrigger>
                  <TabsTrigger value="query" className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    Query
                  </TabsTrigger>
                </TabsList>

                <div className="p-6">
                  <TabsContent value="upload" className="space-y-4">
                    <DocumentUpload onDocumentUploaded={handleDocumentUploaded} />
                  </TabsContent>

                  <TabsContent value="documents" className="space-y-4">
                    <DocumentList 
                      refreshTrigger={refreshTrigger}
                      onDocumentDeleted={handleDocumentDeleted}
                    />
                  </TabsContent>

                  <TabsContent value="query" className="space-y-4">
                    <QueryAnswer documents={documents} />
                  </TabsContent>
                </div>
              </Tabs>
            </div>
          </SignedIn>

          {/* Sign In Prompt for Signed Out Users */}
          <SignedOut>
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 p-12">
              <div className="text-center">
                <FileText className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-slate-800 mb-2">
                  RAG Document Q&A System
                </h2>
                <p className="text-slate-600 mb-6">
                  Please sign in to upload documents and start querying
                </p>
                <SignInButton mode="modal">
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg">
                    Get Started
                  </button>
                </SignInButton>
              </div>
            </div>
          </SignedOut>
        </div>
      </div>
    </ClerkProvider>
  );
}

export default App;