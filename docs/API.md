# API Documentation - Autonotes Generation

## Overview
Complete REST API for lecture transcription, processing, and note generation.

**Base URL:** `http://localhost:8000/api`

---

## Authentication
Currently no authentication required. CORS enabled for local development.

---

## Endpoints

### 1. Health Check
Get API status and health information.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "autonotes-generation",
  "version": "1.0.0"
}
```

---

### 2. API Status
Get API configuration and status.

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "status": "running",
  "debug": true,
  "max_file_size": 500000000,
  "whisper_model": "base",
  "device": "cpu"
}
```

---

## Upload Endpoints

### 3. Upload File
Upload audio or video file for processing.

**Endpoint:** `POST /api/upload/`

**Content-Type:** `multipart/form-data`

**Request:**
```
File: <binary audio/video file>
```

**Supported Formats:** MP3, WAV, M4A, FLAC, OGG, MP4, AVI, MOV, MKV

**Response (Success):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "lecture.mp3",
  "file_path": "./uploads/550e8400-e29b-41d4-a716-446655440000_lecture.mp3",
  "file_size": 15728640,
  "file_size_formatted": "15.00 MB"
}
```

**Response (Error):**
```json
{
  "detail": "File size exceeds limit"
}
```

### 4. Check Upload Status
Check if uploaded file exists.

**Endpoint:** `GET /api/upload/status/{job_id}`

**Response:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "550e8400-e29b-41d4-a716-446655440000_lecture.mp3",
  "file_path": "./uploads/550e8400-e29b-41d4-a716-446655440000_lecture.mp3",
  "file_size": 15728640,
  "exists": true
}
```

---

## Processing Endpoints

### 5. Process File
Transcribe, process, and summarize uploaded file.

**Endpoint:** `POST /api/process/`

**Content-Type:** `application/json`

**Request:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_path": "./uploads/550e8400-e29b-41d4-a716-446655440000_lecture.mp3",
  "language": "en",
  "title": "Advanced Machine Learning"
}
```

**Parameters:**
- `job_id` (string, required): Unique job identifier from upload
- `file_path` (string, required): Path to uploaded file
- `language` (string, optional): Language code (en, es, fr, etc.)
- `title` (string, optional): Lecture title

**Response (Success):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "transcript": {
    "text": "Today we'll discuss machine learning...",
    "duration": 3600,
    "language": "en",
    "segment_count": 150
  },
  "processed_data": {
    "section_count": 25,
    "word_count": 8500,
    "sentence_count": 320,
    "keywords": ["machine learning", "neural networks", "deep learning", ...]
  },
  "summaries": {
    "overall_summary": "This lecture covers...",
    "bullet_point_count": 10,
    "bullet_points": [
      "Introduction to machine learning concepts",
      "Types of machine learning algorithms",
      ...
    ]
  }
}
```

**Response (Error):**
```json
{
  "detail": "Processing failed: [error message]"
}
```

### 6. Check Processing Status
Check if file has been processed.

**Endpoint:** `GET /api/process/status/{job_id}`

**Response:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "transcript_available": true
}
```

---

## Export Endpoints

### 7. Export Notes
Export processed notes in specified format.

**Endpoint:** `POST /api/export/`

**Content-Type:** `application/json`

**Request:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "markdown",
  "title": "Advanced Machine Learning"
}
```

**Parameters:**
- `job_id` (string, required): Processing job ID
- `format` (string, required): Export format - `markdown`, `pdf`, `docx`, or `all`
- `title` (string, optional): Document title

**Response (Single Format):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "markdown",
  "file_path": "./output/550e8400-e29b-41d4-a716-446655440000_Advanced_Machine_Learning.md",
  "file_url": "/api/export/download/550e8400-e29b-41d4-a716-446655440000/markdown"
}
```

**Response (All Formats):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "all",
  "files": {
    "markdown": "./output/550e8400-e29b-41d4-a716-446655440000_Advanced_Machine_Learning.md",
    "pdf": "./output/550e8400-e29b-41d4-a716-446655440000_Advanced_Machine_Learning.pdf",
    "docx": "./output/550e8400-e29b-41d4-a716-446655440000_Advanced_Machine_Learning.docx"
  }
}
```

### 8. Download Exported File
Download previously exported file.

**Endpoint:** `GET /api/export/download/{job_id}/{format}`

**Parameters:**
- `job_id` (string, required): Processing job ID
- `format` (string, required): File format - `markdown`, `pdf`, or `docx`

**Response:** File binary data with appropriate content-type

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Unsupported file format: .xyz"
}
```

### 404 Not Found
```json
{
  "detail": "File not found"
}
```

### 413 Payload Too Large
```json
{
  "detail": "File size exceeds limit"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Processing failed: [error details]"
}
```

---

## Complete Workflow Example

### 1. Upload
```bash
curl -X POST "http://localhost:8000/api/upload/" \
  -F "file=@lecture.mp3"
```
Response: `job_id = "550e8400-e29b-41d4-a716-446655440000"`

### 2. Process
```bash
curl -X POST "http://localhost:8000/api/process/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_path": "./uploads/550e8400-e29b-41d4-a716-446655440000_lecture.mp3",
    "title": "My Lecture"
  }'
```

### 3. Export
```bash
curl -X POST "http://localhost:8000/api/export/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "format": "pdf",
    "title": "My Lecture"
  }'
```

### 4. Download
```bash
curl -X GET "http://localhost:8000/api/export/download/550e8400-e29b-41d4-a716-446655440000/pdf" \
  -o lecture_notes.pdf
```

---

## Rate Limiting
Currently no rate limiting. Rate limiting can be added using FastAPI's SlowAPI.

---

## Response Time Guidelines
- Upload: < 1 second
- Process (30-60 min lecture): 2-10 minutes (depends on file size and model)
- Export: < 5 seconds
- Download: < 1 second

---

## Swagger/OpenAPI
Interactive API documentation available at: `http://localhost:8000/docs`
