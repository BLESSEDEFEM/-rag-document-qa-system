import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  it('renders main heading', () => {
    render(<App />);
    
    const heading = screen.getByText(/RAG Document Q&A System/i);
    expect(heading).toBeInTheDocument();
  });

  it('renders all three main sections', () => {
  render(<App />);
  
  expect(screen.getByRole('heading', { name: /Upload Document/i })).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: /Uploaded Documents/i })).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: /Ask a Question/i })).toBeInTheDocument();
  });
});