import { useState } from 'react';
import { ingestProposal } from '../api/api';
import './Ingest.css';

function Ingest() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
      if (fileExtension !== 'pdf' && fileExtension !== 'docx') {
        setError('Please select a PDF or DOCX file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const response = await ingestProposal(file, title);
      setMessage({
        type: 'success',
        text: response.message || 'Proposal ingested successfully!'
      });
      
      // Reset form
      setFile(null);
      setTitle('');
      e.target.reset();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to ingest proposal. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Ingest R&D Proposal</h1>
      <p className="page-description">
        Upload a PDF or DOCX file containing an R&D proposal. The system will extract the text,
        generate embeddings, and store it for future novelty comparisons.
      </p>

      {message && (
        <div className={`alert alert-${message.type}`}>
          {message.text}
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="ingest-form">
        <div className="form-group">
          <label htmlFor="title" className="form-label">
            Proposal Title (Optional)
          </label>
          <input
            type="text"
            id="title"
            className="form-input"
            placeholder="Enter proposal title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={loading}
          />
          <small className="form-hint">
            If not provided, the filename will be used as the title
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="file" className="form-label">
            Upload Document <span className="required">*</span>
          </label>
          <div className="file-input-wrapper">
            <input
              type="file"
              id="file"
              className="file-input"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              disabled={loading}
              required
            />
            <label htmlFor="file" className="file-input-label">
              {file ? file.name : 'Choose PDF or DOCX file'}
            </label>
          </div>
          <small className="form-hint">
            Supported formats: PDF, DOCX (Max size: 10MB)
          </small>
        </div>

        <button type="submit" className="btn btn-submit" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner-small"></span>
              Processing...
            </>
          ) : (
            'Ingest Proposal'
          )}
        </button>
      </form>

      <div className="info-box">
        <h3>📋 How it works:</h3>
        <ol>
          <li>Upload your R&D proposal document (PDF or DOCX)</li>
          <li>The system extracts text from the document</li>
          <li>AI generates a 768-dimensional semantic embedding</li>
          <li>The proposal is stored in PostgreSQL with pgvector</li>
          <li>It's now available for novelty comparisons</li>
        </ol>
      </div>
    </div>
  );
}

export default Ingest;
