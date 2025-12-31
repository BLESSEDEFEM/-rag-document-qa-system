import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DocumentUpload from '../components/DocumentUpload';

vi.mock('../services/api');

describe('DocumentUpload', () => {
  it('renders upload component', () => {
    render(<DocumentUpload onUploadSuccess={vi.fn()} />);
    
    expect(screen.getByText(/Upload Document/i)).toBeInTheDocument();
  });

  it('shows disabled upload button initially', () => {
    render(<DocumentUpload onUploadSuccess={vi.fn()} />);
    
    const button = screen.getByRole('button', { name: /upload/i });
    expect(button).toBeDisabled();
  });
});