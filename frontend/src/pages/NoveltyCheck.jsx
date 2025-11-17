import { useState } from 'react';
import { checkNovelty, checkNoveltyFromFile } from '../api/api';
import './NoveltyCheck.css';

function NoveltyCheck() {
  const [inputMethod, setInputMethod] = useState('text'); // 'text' or 'file'
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
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
    
    if (inputMethod === 'text' && (!text || text.length < 10)) {
      setError('Please enter at least 10 characters of text');
      return;
    }
    
    if (inputMethod === 'file' && !file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      if (inputMethod === 'text') {
        response = await checkNovelty(text);
      } else {
        response = await checkNoveltyFromFile(file);
      }
      
      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to check novelty. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#48bb78'; // green
    if (score >= 60) return '#4299e1'; // blue
    if (score >= 40) return '#ed8936'; // orange
    return '#f56565'; // red
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Check Novelty Score</h1>
      <p className="page-description">
        Evaluate how novel your R&D proposal is by comparing it against stored proposals.
        Higher scores indicate more novelty.
      </p>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="input-method-selector">
        <button
          className={`method-btn ${inputMethod === 'text' ? 'active' : ''}`}
          onClick={() => setInputMethod('text')}
        >
          📝 Paste Text
        </button>
        <button
          className={`method-btn ${inputMethod === 'file' ? 'active' : ''}`}
          onClick={() => setInputMethod('file')}
        >
          📄 Upload File
        </button>
      </div>

      <form onSubmit={handleSubmit} className="novelty-form">
        {inputMethod === 'text' ? (
          <div className="form-group">
            <label htmlFor="text" className="form-label">
              Proposal Text <span className="required">*</span>
            </label>
            <textarea
              id="text"
              className="form-textarea"
              placeholder="Paste your R&D proposal text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
              rows={12}
              required
            />
            <small className="form-hint">
              Minimum 10 characters. More text provides better accuracy.
            </small>
          </div>
        ) : (
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
              Supported formats: PDF, DOCX
            </small>
          </div>
        )}

        <button type="submit" className="btn btn-submit" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner-small"></span>
              Analyzing...
            </>
          ) : (
            '🔍 Check Novelty'
          )}
        </button>
      </form>

      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Analyzing proposal novelty...</p>
        </div>
      )}

      {result && (
        <div className="results-container">
          <div className="score-card" style={{ borderColor: getScoreColor(result.novelty_score) }}>
            <div className="score-label">Novelty Score</div>
            <div className="score-value" style={{ color: getScoreColor(result.novelty_score) }}>
              {result.novelty_score.toFixed(1)}
            </div>
            <div className="score-max">out of 100</div>
            <div className="score-interpretation">
              {result.interpretation}
            </div>
          </div>

          <div className="stats-row">
            <div className="stat-item">
              <div className="stat-label">Total Proposals Checked</div>
              <div className="stat-value">{result.total_proposals_checked}</div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Similar Proposals Found</div>
              <div className="stat-value">{result.similar_proposals.length}</div>
            </div>
          </div>

          {result.similar_proposals.length > 0 && (
            <div className="similar-proposals">
              <h3>Most Similar Proposals</h3>
              <div className="proposals-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Similarity</th>
                      <th>Match Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.similar_proposals.map((proposal) => (
                      <tr key={proposal.id}>
                        <td>{proposal.id}</td>
                        <td className="proposal-title">{proposal.title}</td>
                        <td>
                          <div className="similarity-bar-container">
                            <div 
                              className="similarity-bar"
                              style={{ 
                                width: `${proposal.similarity * 100}%`,
                                backgroundColor: getScoreColor((1 - proposal.similarity) * 100)
                              }}
                            />
                            <span className="similarity-text">
                              {(proposal.similarity * 100).toFixed(1)}%
                            </span>
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${proposal.similarity > 0.7 ? 'badge-high' : proposal.similarity > 0.4 ? 'badge-medium' : 'badge-low'}`}>
                            {proposal.similarity > 0.7 ? 'High' : proposal.similarity > 0.4 ? 'Medium' : 'Low'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="info-box">
            <h4>📊 Understanding Your Score:</h4>
            <ul>
              <li><strong>80-100:</strong> Highly novel - Your proposal is very unique</li>
              <li><strong>60-79:</strong> Novel - Significant unique elements present</li>
              <li><strong>40-59:</strong> Moderately novel - Some similarities exist</li>
              <li><strong>20-39:</strong> Low novelty - Quite similar to existing work</li>
              <li><strong>0-19:</strong> Very low novelty - Very similar to existing proposals</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default NoveltyCheck;
