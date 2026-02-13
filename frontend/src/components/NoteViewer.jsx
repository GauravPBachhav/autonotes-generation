import React, { useState } from 'react';
import axios from 'axios';
import './NoteViewer.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function NoteViewer({ processingData, jobId, title }) {
  const [activeTab, setActiveTab] = useState('transcript');
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);
  const [expandedTopics, setExpandedTopics] = useState({});

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

  const toggleTopic = (idx) => {
    setExpandedTopics(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const structuredNotes = processingData.structured_notes || {};
  const topics = structuredNotes.topics || processingData.processed_data?.sections || [];
  const definitions = structuredNotes.definitions || [];
  const keyTakeaways = structuredNotes.key_takeaways || [];
  const quickRevision = structuredNotes.quick_revision || [];
  const keywords = processingData.processed_data?.keywords || [];
  const keyPhrases = processingData.processed_data?.key_phrases || [];
  const bulletPoints = processingData.summaries?.bullet_points || [];

  return (
    <div className="note-viewer">
      {/* ─── Header ─── */}
      <div className="viewer-header">
        <div className="header-left">
          <h2>📚 {title}</h2>
          <div className="header-stats">
            <span className="stat-badge">⏱️ {processingData.transcript?.duration?.toFixed(0) || 0}s</span>
            <span className="stat-badge">📝 {processingData.processed_data?.word_count || 0} words</span>
            <span className="stat-badge">📌 {topics.length} topics</span>
            <span className="stat-badge">🌐 {processingData.transcript?.language || 'N/A'}</span>
          </div>
        </div>
        <div className="export-buttons">
          <button onClick={() => handleExport('markdown')} disabled={exporting} className="export-btn markdown">📝 Markdown</button>
          <button onClick={() => handleExport('pdf')} disabled={exporting} className="export-btn pdf">📄 PDF</button>
          <button onClick={() => handleExport('docx')} disabled={exporting} className="export-btn docx">📋 Word</button>
          <button onClick={() => handleExport('all')} disabled={exporting} className="export-btn all">📦 All</button>
        </div>
      </div>

      {exportError && <div className="export-error">{exportError}</div>}

      {/* ─── Tab Navigation ─── */}
      <div className="tabs">
        <button className={`tab ${activeTab === 'transcript' ? 'active' : ''}`} onClick={() => setActiveTab('transcript')}>
          🎙️ Original Transcription
        </button>
        <button className={`tab ${activeTab === 'notes' ? 'active' : ''}`} onClick={() => setActiveTab('notes')}>
          📝 Structured Notes
        </button>
      </div>

      {/* ─── Content ─── */}
      <div className="content">

        {/* ═══ TAB 1: Original Transcription (as-is) ═══ */}
        {activeTab === 'transcript' && (
          <div className="section transcript-section">
            <div className="section-header">
              <h3>🎙️ Original Transcription</h3>
              <p className="section-subtitle">Complete word-by-word transcript from audio — preserved as-is</p>
            </div>
            <div className="transcript-box">
              {processingData.transcript?.text || 'No transcription available.'}
            </div>
            <div className="transcript-meta">
              <span>Duration: <strong>{processingData.transcript?.duration?.toFixed(0) || 0}s</strong></span>
              <span>Segments: <strong>{processingData.transcript?.segment_count || 0}</strong></span>
              <span>Language: <strong>{processingData.transcript?.language || 'N/A'}</strong></span>
            </div>
          </div>
        )}

        {/* ═══ TAB 2: Structured Notes ═══ */}
        {activeTab === 'notes' && (
          <div className="section notes-section">

            {/* ── Summary ── */}
            <div className="notes-card summary-card">
              <div className="card-header">
                <h3>📋 Summary</h3>
              </div>
              <div className="card-body">
                <p>{processingData.summaries?.overall_summary || 'No summary available.'}</p>
              </div>
            </div>

            {/* ── Topic-wise Notes ── */}
            <div className="notes-card topics-card">
              <div className="card-header">
                <h3>📌 Topic-wise Notes</h3>
                <span className="topic-count">{topics.length} topics detected</span>
              </div>
              <div className="card-body">
                {topics.map((topic, idx) => (
                  <div key={idx} className={`topic-item ${expandedTopics[idx] ? 'expanded' : ''}`}>
                    <div className="topic-header" onClick={() => toggleTopic(idx)}>
                      <span className="topic-number">{idx + 1}</span>
                      <h4>{topic.title || `Topic ${idx + 1}`}</h4>
                      <span className="topic-toggle">{expandedTopics[idx] ? '▲' : '▼'}</span>
                    </div>
                    {expandedTopics[idx] && (
                      <div className="topic-content">
                        {topic.bullet_points && topic.bullet_points.length > 0 ? (
                          <ul className="topic-bullets">
                            {topic.bullet_points.map((point, pIdx) => (
                              <li key={pIdx}>{point}</li>
                            ))}
                          </ul>
                        ) : (
                          <p className="topic-text">{topic.content || topic.text || ''}</p>
                        )}
                        {topic.keywords && topic.keywords.length > 0 && (
                          <div className="topic-keywords">
                            <strong>Key terms: </strong>
                            {topic.keywords.map((kw, kIdx) => (
                              <span key={kIdx} className="mini-tag">{kw}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* ── Key Definitions ── */}
            {definitions.length > 0 && (
              <div className="notes-card definitions-card">
                <div className="card-header">
                  <h3>📖 Key Definitions</h3>
                </div>
                <div className="card-body">
                  <div className="definitions-grid">
                    {definitions.map((def_, idx) => (
                      <div key={idx} className="definition-item">
                        <span className="def-term">{def_.term}</span>
                        <span className="def-text">{def_.definition}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── Key Takeaways ── */}
            {keyTakeaways.length > 0 && (
              <div className="notes-card takeaways-card">
                <div className="card-header">
                  <h3>⭐ Key Takeaways</h3>
                </div>
                <div className="card-body">
                  <ol className="takeaways-list">
                    {keyTakeaways.map((point, idx) => (
                      <li key={idx}>{point}</li>
                    ))}
                  </ol>
                </div>
              </div>
            )}

            {/* ── Important Points (from summarizer) ── */}
            {bulletPoints.length > 0 && (
              <div className="notes-card bullets-card">
                <div className="card-header">
                  <h3>🔑 Important Points</h3>
                </div>
                <div className="card-body">
                  <ul className="important-points">
                    {bulletPoints.map((point, idx) => (
                      <li key={idx}>{point}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* ── Quick Revision ── */}
            {quickRevision.length > 0 && (
              <div className="notes-card revision-card">
                <div className="card-header">
                  <h3>🔄 Quick Revision</h3>
                </div>
                <div className="card-body">
                  <ul className="revision-list">
                    {quickRevision.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* ── Keywords & Key Phrases ── */}
            <div className="notes-card keywords-card">
              <div className="card-header">
                <h3>🏷️ Keywords & Key Phrases</h3>
              </div>
              <div className="card-body">
                {keywords.length > 0 && (
                  <div className="tag-section">
                    <h4>Keywords</h4>
                    <div className="tag-cloud">
                      {keywords.map((kw, idx) => (
                        <span key={idx} className="keyword-tag">{kw}</span>
                      ))}
                    </div>
                  </div>
                )}
                {keyPhrases.length > 0 && (
                  <div className="tag-section">
                    <h4>Key Phrases</h4>
                    <div className="tag-cloud">
                      {keyPhrases.map((kp, idx) => (
                        <span key={idx} className="phrase-tag">{kp}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* ── Stats ── */}
            <div className="notes-card stats-card">
              <div className="card-header">
                <h3>📊 Statistics</h3>
              </div>
              <div className="card-body">
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-value">{processingData.processed_data?.word_count || 0}</div>
                    <div className="stat-label">Words</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{processingData.processed_data?.sentence_count || 0}</div>
                    <div className="stat-label">Sentences</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{topics.length}</div>
                    <div className="stat-label">Topics</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{processingData.transcript?.duration?.toFixed(0) || 0}s</div>
                    <div className="stat-label">Duration</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{bulletPoints.length}</div>
                    <div className="stat-label">Key Points</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{definitions.length}</div>
                    <div className="stat-label">Definitions</div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
