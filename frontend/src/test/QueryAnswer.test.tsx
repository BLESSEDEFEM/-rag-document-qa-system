import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import QueryAnswer from '../components/QueryAnswer';
import * as api from '../services/api';

vi.mock('../services/api');

describe('QueryAnswer', () => {
  it('renders query form', () => {
    render(<QueryAnswer />);
    
    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument();
    expect(screen.getByText(/ask question/i)).toBeInTheDocument();
  });

  it('shows error for empty query', async () => {
    render(<QueryAnswer />);
    
    const button = screen.getByText(/ask question/i);
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText(/please enter a question/i)).toBeInTheDocument();
    });
  });

  it('displays answer from API', async () => {
    const mockAnswer = vi.spyOn(api, 'answerQuestion').mockResolvedValue({
      success: true,
      answer: 'Machine learning is...',
      sources: [],
      chunks_used: 2
    } as any);

    render(<QueryAnswer />);
    
    const textarea = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(textarea, { target: { value: 'What is ML?' } });
    
    const button = screen.getByText(/ask question/i);
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText(/machine learning is/i)).toBeInTheDocument();
    });
  });

  it('shows chat history', async () => {
    vi.spyOn(api, 'answerQuestion').mockResolvedValue({
      success: true,
      answer: 'Test answer',
      sources: []
    } as any);

    render(<QueryAnswer />);
    
    const textarea = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(textarea, { target: { value: 'Test question' } });
    
    const button = screen.getByText(/ask question/i);
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText(/test question/i)).toBeInTheDocument();
      expect(screen.getByText(/test answer/i)).toBeInTheDocument();
    });
  });
});