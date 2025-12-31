import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import QueryAnswer from '../components/QueryAnswer';
import * as api from '../services/api';

vi.mock('../services/api');

describe('QueryAnswer', () => {
  it('renders query form', () => {
    render(<QueryAnswer />);
    
    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument();
  });

  it('shows button in disabled state initially', () => {
    render(<QueryAnswer />);
    
    const button = screen.getByRole('button', { name: /ask question/i });
    expect(button).toBeDisabled();
  });

  it('enables button when query is entered', async () => {
    render(<QueryAnswer />);
    
    const textarea = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(textarea, { target: { value: 'What is ML?' } });
    
    const button = screen.getByRole('button', { name: /ask question/i });
    expect(button).not.toBeDisabled();
  });

  it('displays answer from API', async () => {
    vi.spyOn(api, 'answerQuestion').mockResolvedValue({
      success: true,
      answer: 'Machine learning is a subset of AI.',
      query: 'What is ML?',
      sources: [],
      chunks_used: 2,
      retrieval_stats: {
        chunks_retrieved: 5,
        chunks_after_filter: 2,
        top_k: 5,
        min_score: 0.3
      }
    });

    render(<QueryAnswer />);
    
    const textarea = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(textarea, { target: { value: 'What is ML?' } });
    
    const button = screen.getByRole('button', { name: /ask question/i });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText(/Machine learning is a subset of AI/i)).toBeInTheDocument();
    });
  });
});