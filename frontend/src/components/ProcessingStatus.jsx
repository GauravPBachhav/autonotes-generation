import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ProcessingStatus.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function ProcessingStatus({ jobId, filename, onProcessingComplete }) {
  const [status, setStatus] = useState('processing');
  const [progress, setProgress] = useState(0);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const startProcessing = async () => {
      try {
        // Find the file first
        const uploadStatusResponse = await axios.get(`${API_URL}/upload/status/${jobId}`);
        
        if (!uploadStatusResponse.data.exists) {
          setError('File not found. Please upload again.');
          return;
        }

        const filePath = uploadStatusResponse.data.file_path;

        // Start processing
        const processResponse = await axios.post(`${API_URL}/process/`, {
          job_id: jobId,
          file_path: filePath,
          title: filename.split('.')[0],
        });

        if (processResponse.data.success) {
          setData(processResponse.data);
          setStatus('completed');
          setProgress(100);
          onProcessingComplete(processResponse.data);
        }
      } catch (err) {
        console.error('Processing error:', err);
        setError(err.response?.data?.detail || 'Processing failed. Please try again.');
        setStatus('error');
      }
    };

    if (jobId) {
      startProcessing();
    }
  }, [jobId]);

  const getProgressSteps = () => {
    if (status === 'processing') {
      return [
        { name: 'Uploading', completed: true },
        { name: 'Transcribing', completed: progress > 25 },
        { name: 'Processing', completed: progress > 50 },
        { name: 'Summarizing', completed: progress > 75 },
        { name: 'Generating', completed: progress > 90 },
      ];
    }
    return [];
  };

  if (status === 'completed') {
    return (
      <div className="processing-status">
        <div className="success-container">
          <div className="success-icon">✓</div>
          <h2>Processing Complete!</h2>
          {data && (
            <div className="results-summary">
              <div className="result-item">
                <span className="label">Duration:</span>
                <span className="value">{data.transcript.duration.toFixed(0)}s</span>
              </div>
              <div className="result-item">
                <span className="label">Word Count:</span>
                <span className="value">{data.processed_data.word_count}</span>
              </div>
              <div className="result-item">
                <span className="label">Sections:</span>
                <span className="value">{data.processed_data.section_count}</span>
              </div>
              <div className="result-item">
                <span className="label">Key Points:</span>
                <span className="value">{data.summaries.bullet_point_count}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="processing-status">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h2>Processing Failed</h2>
          <p className="error-message">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="processing-status">
      <div className="progress-container">
        <h2>Processing Your Lecture...</h2>
        
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <p className="progress-text">{progress}% Complete</p>

        <div className="steps">
          {getProgressSteps().map((step, idx) => (
            <div key={idx} className={`step ${step.completed ? 'completed' : ''}`}>
              <div className="step-icon">{step.completed ? '✓' : '○'}</div>
              <div className="step-name">{step.name}</div>
            </div>
          ))}
        </div>

        <p className="processing-message">
          This may take a few minutes depending on file size...
        </p>
      </div>
    </div>
  );
}
