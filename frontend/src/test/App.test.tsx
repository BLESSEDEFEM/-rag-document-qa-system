import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ClerkProvider } from '@clerk/clerk-react';
import App from '../App';

// Mock Clerk environment
vi.mock('@clerk/clerk-react', async () => {
  const actual = await vi.importActual('@clerk/clerk-react');
  return {
    ...actual,
    useAuth: () => ({
      isLoaded: true,
      isSignedIn: false,
      getToken: vi.fn(),
    }),
  };
});

const PUBLISHABLE_KEY = 'pk_test_mock_key_for_testing';

describe('App Component', () => {
  it('renders main heading', () => {
    render(
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <App />
      </ClerkProvider>
    );
    
    expect(screen.getByText(/RAG Document Q&A System/i)).toBeInTheDocument();
  });

  it('shows sign in prompt when not authenticated', () => {
    render(
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <App />
      </ClerkProvider>
    );
    
    expect(screen.getByText(/Sign in to access your documents/i)).toBeInTheDocument();
  });
});