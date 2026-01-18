import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function FileUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file) => {
    setError(null);
    
    // Validate file type
    const supportedFormats = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'video/mp4', 'video/avi', 'video/quicktime'];
    if (!supportedFormats.some(fmt => file.type.includes(fmt.split('/')[1]) || file.name.includes('mp3') || file.name.includes('wav'))) {
      setError('Unsupported file format. Please upload audio or video files.');
      return;
    }

    // Validate file size (max 500MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size exceeds 500MB limit.');
      return;
    }

    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        },
      });

      if (response.data.success) {
        onUploadSuccess({
          job_id: response.data.job_id,
          filename: response.data.filename,
          file_path: response.data.file_path,
          file_size: response.data.file_size_formatted,
        });
        setUploadProgress(0);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📹</div>
        <h2>Upload Lecture Recording</h2>
        <p>Drag and drop your audio or video file here</p>
        <p className="file-types">Supported: MP3, WAV, MP4, AVI, MOV (max 500MB)</p>
        
        <input
          type="file"
          id="file-input"
          onChange={handleFileChange}
          disabled={isUploading}
          accept=".mp3,.wav,.mp4,.avi,.mov,.mkv,.flac,.ogg,.m4a"
        />
        <label htmlFor="file-input" className="browse-button">
          Browse Files
        </label>
      </div>

      {isUploading && (
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
          </div>
          <p>{uploadProgress}% uploaded...</p>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
}
