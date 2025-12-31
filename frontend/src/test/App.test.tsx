import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock the entire Clerk module
vi.mock('@clerk/clerk-react', () => ({
  ClerkProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SignedIn: () => null,
  SignedOut: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SignInButton: ({ children }: { children: React.ReactNode }) => <button>{children}</button>,
  UserButton: () => <div>User Button</div>,
  useAuth: () => ({
    isLoaded: true,
    isSignedIn: false,
    getToken: vi.fn().mockResolvedValue(null),
  }),
}));

describe('App Component', () => {
  it('renders main heading', () => {
    render(<App />);
    
    expect(screen.getByText(/RAG Document Q&A System/i)).toBeInTheDocument();
  });

  it('shows sign in prompt when not authenticated', () => {
    render(<App />);
    
    expect(screen.getByText(/Sign in to access your documents/i)).toBeInTheDocument();
  });
});