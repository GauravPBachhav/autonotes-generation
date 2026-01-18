import React, { useState } from 'react';
import axios from 'axios';
import './NoteViewer.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function NoteViewer({ processingData, jobId, title }) {
  const [activeTab, setActiveTab] = useState('summary');
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  const handleExport = async (format) => {
    try {
      setExporting(true);
      setExportError(null);

      const response = await axios.post(`${API_URL}/export/`, {
        job_id: jobId,
        format: format,
        title: title,
      });

      if (response.data.success) {
        // Download file - use full URL
        const downloadUrl = `http://localhost:8000${response.data.file_url}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = response.data.file_path.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      setExportError(err.response?.data?.detail || 'Export failed');
      console.error('Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="note-viewer">
      <div className="viewer-header">
        <h2>{title}</h2>
        <div className="export-buttons">
          <button 
            onClick={() => handleExport('markdown')} 
            disabled={exporting}
            className="export-btn markdown"
          >
            📝 Markdown
          </button>
          <button 
            onClick={() => handleExport('pdf')} 
            disabled={exporting}
            className="export-btn pdf"
          >
            📄 PDF
          </button>
          <button 
            onClick={() => handleExport('docx')} 
            disabled={exporting}
            className="export-btn docx"
          >
            📋 Word
          </button>
          <button 
            onClick={() => handleExport('all')} 
            disabled={exporting}
            className="export-btn all"
          >
            📦 All
          </button>
        </div>
      </div>

      {exportError && <div className="export-error">{exportError}</div>}

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'simplified' ? 'active' : ''}`}
          onClick={() => setActiveTab('simplified')}
        >
          📝 Simplified Notes
        </button>
        <button 
          className={`tab ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          🎙️ Raw Transcript
        </button>
        <button 
          className={`tab ${activeTab === 'keypoints' ? 'active' : ''}`}
          onClick={() => setActiveTab('keypoints')}
        >
          ⭐ Key Points
        </button>
        <button 
          className={`tab ${activeTab === 'keywords' ? 'active' : ''}`}
          onClick={() => setActiveTab('keywords')}
        >
          🏷️ Keywords
        </button>
      </div>

      <div className="content">
        {activeTab === 'simplified' && (
          <div className="section">
            <h3>📝 Simplified Notes</h3>
            <p className="note-description">Easy-to-read, organized version with key concepts</p>
            
            <div className="simplified-section">
              <h4>Executive Summary</h4>
              <p>{processingData.summaries.overall_summary}</p>
            </div>
            
            <div className="simplified-section">
              <h4>Main Topics</h4>
              {processingData.processed_data.sections && processingData.processed_data.sections.slice(0, 5).map((section, idx) => (
                <div key={idx} className="topic-card">
                  <h5>Topic {idx + 1}</h5>
                  <p>{section.text && section.text.substring(0, 300)}...</p>
                </div>
              ))}
            </div>

            <div className="stats">
              <div className="stat">
                <span className="stat-label">Duration:</span>
                <span className="stat-value">{processingData.transcript.duration.toFixed(0)}s</span>
              </div>
              <div className="stat">
                <span className="stat-label">Words:</span>
                <span className="stat-value">{processingData.processed_data.word_count}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Topics:</span>
                <span className="stat-value">{processingData.processed_data.section_count}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'raw' && (
          <div className="section">
            <h3>🎙️ Raw Transcript</h3>
            <p className="note-description">Complete word-by-word transcription from audio</p>
            <p className="full-transcript">{processingData.transcript.text}</p>
          </div>
        )}

        {activeTab === 'keypoints' && (
          <div className="section">
            <h3>⭐ Key Points</h3>
            <ul className="bullet-points">
              {processingData.summaries.bullet_points.map((point, idx) => (
                <li key={idx}>{point}</li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'keywords' && (
          <div className="section">
            <h3>🏷️ Key Terms & Concepts</h3>
            <div className="keywords">
              {processingData.processed_data.keywords.map((keyword, idx) => (
                <span key={idx} className="keyword-tag">{keyword}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
