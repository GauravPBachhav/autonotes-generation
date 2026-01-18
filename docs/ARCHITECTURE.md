# System Architecture - Autonotes Generation

## High-Level Architecture

```
User (Web Browser)
       ↓
   Frontend (React)
       ↓
   [Upload File]
       ↓
   FastAPI Server (Backend)
       ↓
   ├─ Transcriber (Whisper)
   ├─ Processor (NLTK/spaCy)
   ├─ Summarizer (Transformers)
   └─ Note Generator
       ↓
   Output: PDF/Docx/Markdown
       ↓
   User Downloads Notes
```

## Component Details

### 1. Frontend Layer
- **Technology**: React.js
- **Responsibility**: User interface, file upload, progress display
- **Files**: Upload, processing status, note viewer

### 2. Backend Layer

#### API Server (FastAPI)
- Handles HTTP requests
- Validates uploads
- Routes to processing modules

#### Processing Modules

**Transcriber**
- Input: Audio/Video file
- Output: Text transcript with timestamps
- Tech: OpenAI Whisper API

**Processor**
- Input: Raw transcript
- Tasks:
  - Remove filler words/stutters
  - Segment by sentences/paragraphs
  - Detect section breaks
  - Extract key phrases
- Output: Structured text

**Summarizer**
- Input: Segmented text
- Tech: BART/T5 models (Hugging Face Transformers)
- Output: Summary (30-50% of original)

**Note Generator**
- Input: Original text + summary + key points
- Formats output:
  - Markdown
  - PDF
  - Docx
- Output: Formatted document

### 3. Storage Layer
- **Uploads**: Temporary storage for input files
- **Processed Data**: Cache transcripts & summaries
- **Notes**: Final output files
- **Metadata**: Database (SQLite/PostgreSQL)

### 4. Task Queue (Optional - for scalability)
- **Tech**: Celery + Redis
- **Purpose**: Handle long-running jobs asynchronously
- **Flow**: User → Submit Job → Queue → Worker → Complete → Notify User

---

## Data Flow

### Processing Pipeline

```
Step 1: Upload
├─ Validate file (format, size)
├─ Store file temporarily
└─ Return job_id

Step 2: Transcription
├─ Load audio file
├─ Extract audio from video (if needed)
├─ Run Whisper model
├─ Generate transcript + timestamps
└─ Cache transcript

Step 3: Text Processing
├─ Clean text (remove filler words)
├─ Segment into sections
├─ Extract key phrases & entities
└─ Structure output

Step 4: Summarization
├─ Split text into chunks
├─ Run summarizer model per chunk
├─ Combine summaries
├─ Extract key points
└─ Structure summary

Step 5: Note Generation
├─ Combine transcript, summary, key points
├─ Format (Markdown/PDF/Docx)
├─ Add metadata (timestamps, speaker info)
└─ Store & return file

Step 6: Export
├─ User selects format
├─ Generate document
└─ Return downloadable file
```

---

## Database Schema (Optional)

### Jobs Table
```sql
CREATE TABLE jobs (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36),
  filename VARCHAR(255),
  status VARCHAR(20),  -- pending, processing, completed, failed
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  file_path TEXT
);
```

### Notes Table
```sql
CREATE TABLE notes (
  id VARCHAR(36) PRIMARY KEY,
  job_id VARCHAR(36) FOREIGN KEY,
  transcript TEXT,
  summary TEXT,
  key_points TEXT,
  metadata JSON,
  created_at TIMESTAMP
);
```

---

## Deployment Architecture

### Development
```
Local Machine
├─ Frontend (npm run dev)
└─ Backend (python main.py)
```

### Production (Docker)
```
Docker Compose
├─ Frontend Container
├─ Backend Container
├─ Redis Container (optional)
├─ PostgreSQL Container (optional)
└─ Nginx (reverse proxy)
```

### Cloud Deployment (AWS/GCP/Azure)
```
Load Balancer
    ↓
├─ Frontend (S3 + CloudFront)
├─ API Server (ECS/Kubernetes)
├─ Task Queue (SQS/Celery)
├─ Database (RDS/Cloud SQL)
└─ Storage (S3/Cloud Storage)
```

---

## Performance Optimization

### Caching
- Cache Whisper model in memory
- Cache transformer models
- Cache summarization results

### Parallelization
- Process audio chunks in parallel
- Use GPU for model inference
- Async API calls

### Resource Management
- Limit concurrent jobs
- Auto-scale workers
- Memory pooling

---

## Security Measures

- [ ] File upload validation (extension, size, MIME type)
- [ ] Virus scanning (optional)
- [ ] HTTPS/TLS for data in transit
- [ ] Input sanitization
- [ ] Rate limiting on API endpoints
- [ ] Auto-delete uploads after processing
- [ ] User authentication (optional)

---

## Error Handling

```
Error Types:
├─ Upload Errors (file too large, invalid format)
├─ Processing Errors (out of memory, timeout)
├─ Model Errors (model load fail, inference error)
└─ Export Errors (format conversion fail)

Recovery:
├─ Retry with smaller batch size
├─ Fallback to simpler model
└─ Graceful error messages to user
```

---

## Scalability Considerations

1. **Horizontal Scaling**: Add more worker nodes
2. **Queue-based Processing**: Use Celery for job distribution
3. **Caching Layer**: Redis for frequently accessed data
4. **CDN**: Serve frontend assets globally
5. **Database Optimization**: Indexing, query optimization
6. **Model Optimization**: Quantization, distillation for faster inference

---

## Monitoring & Logging

- Application logs (FastAPI)
- Error tracking (Sentry - optional)
- Performance metrics (Prometheus - optional)
- User analytics (optional)

---

## Timeline & Milestones

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | Week 1-2 | Setup, architecture planning |
| Phase 2 | Week 3-4 | Backend core modules |
| Phase 3 | Week 5-6 | Frontend development |
| Phase 4 | Week 7-8 | Integration & testing |
| Phase 5 | Week 9-10 | Optimization & deployment |
