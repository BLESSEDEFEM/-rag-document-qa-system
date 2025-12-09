import { useState } from 'react';
import { uploadDocument } from '../services/api';

function DocumentUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setSuccess(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await uploadDocument(file);
      setSuccess(`Uploaded: ${result.filename}`);
      setFile(null);
      
      // Reset file input
      document.getElementById('file-input').value = '';
      
      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={styles.container}>
        <h2 style={styles.title}>📤 Upload Document</h2>

        <div style={styles.uploadBox}>
            <input
              id="file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              style={styles.fileInput}
            />

            {file && (
                <p style={styles.fileName}>Selected: {file.name}</p>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              style={{
                ...styles.button,
                ...((!file || uploading) && styles.buttonDisabled),
              }}
            >
              {uploading ? '⏳ Uploading...' : '📤 Upload'}
            </button> 
        </div>

        {error && <div style={styles.error}>{error}</div>}
        {success && <div style={styles.success}>{success}</div>}
    </div>
  );
}       

      
const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  title: {
    marginTop: 0,
    color: '#333',
  },
  uploadBox: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    border: '2px dashed #ccc',
  },
  fileInput: {
    marginBottom: '10px',
    display: 'block',
    width: '100%',
  },
  fileName: {
    color: '#666',
    fontSize: '14px',
    marginBottom: '10px',
  },
  button: {
    backgroundColor: '#4CAF50',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  error: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px',
  },
  success: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#e8f5e9',
    color: '#2e7d32',
    borderRadius: '4px',
  },
};

export default DocumentUpload;