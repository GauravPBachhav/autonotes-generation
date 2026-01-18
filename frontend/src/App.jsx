import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ProcessingStatus from './components/ProcessingStatus';
import NoteViewer from './components/NoteViewer';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('upload'); // upload, processing, viewer
  const [uploadData, setUploadData] = useState(null);
  const [processingData, setProcessingData] = useState(null);

  const handleUploadSuccess = (data) => {
    setUploadData(data);
    setCurrentStep('processing');
  };

  const handleProcessingComplete = (data) => {
    setProcessingData(data);
    setCurrentStep('viewer');
  };

  const handleStartOver = () => {
    setCurrentStep('upload');
    setUploadData(null);
    setProcessingData(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎓 Autonotes Generation</h1>
          <p>Automatically generate structured notes from lecture recordings</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {currentStep === 'upload' && (
            <div className="step-container">
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>
          )}

          {currentStep === 'processing' && uploadData && (
            <div className="step-container">
              <ProcessingStatus
                jobId={uploadData.job_id}
                filename={uploadData.filename}
                onProcessingComplete={handleProcessingComplete}
              />
            </div>
          )}

          {currentStep === 'viewer' && processingData && (
            <div className="step-container">
              <NoteViewer
                processingData={processingData}
                jobId={uploadData.job_id}
                title={uploadData.filename.split('.')[0]}
              />
              <button className="start-over-btn" onClick={handleStartOver}>
                ↻ Process Another Lecture
              </button>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 Autonotes Generation. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
