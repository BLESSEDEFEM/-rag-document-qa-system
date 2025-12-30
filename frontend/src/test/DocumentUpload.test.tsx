import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DocumentUpload from '../components/DocumentUpload';
import * as api from '../services/api';

vi.mock('../services/api');

describe('DocumentUpload', () => {
  it('renders upload form', () => {
    render(<DocumentUpload onUploadSuccess={vi.fn()} />);
    
    expect(screen.getByText(/upload document/i)).toBeInTheDocument();
  });

  it('shows error for invalid file type', async () => {
    render(<DocumentUpload onUploadSuccess={vi.fn()} />);
    
    const file = new File(['test'], 'test.exe', { type: 'application/x-msdownload' });
    const input = screen.getByLabelText(/click to upload/i) as HTMLInputElement;
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
    });
  });

  it('uploads file successfully', async () => {
    const mockUpload = vi.spyOn(api, 'uploadDocument').mockResolvedValue({
      document_id: 1,
      filename: 'test.pdf',
      status: 'ready'
    } as any);

    const onSuccess = vi.fn();
    render(<DocumentUpload onUploadSuccess={onSuccess} />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/click to upload/i) as HTMLInputElement;
    
    fireEvent.change(input, { target: { files: [file] } });
    
    const uploadButton = screen.getByText(/upload/i);
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      expect(mockUpload).toHaveBeenCalled();
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});