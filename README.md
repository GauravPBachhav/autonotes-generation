# Autonotes Generation from Lectures

## Project Overview
Autonotes is a diploma project designed to automatically generate structured notes from lecture recordings. The system extracts speech from audio/video, processes the transcript, and produces organized, summarized notes with timestamps, key points, and action items.

---

## Project Objectives
1. **Speech-to-Text**: Convert lecture audio to text transcripts
2. **Text Processing**: Clean, segment, and structure transcripts
3. **Summarization**: Generate concise summaries from lengthy lectures
4. **Note Generation**: Create formatted notes (PDF, Docx, Markdown)
5. **User Experience**: Simple web interface for easy usage

---

## Project Structure
```
autonotes-generation/
├── backend/                    # Python FastAPI backend
│   ├── modules/               # Core processing modules
│   │   ├── __init__.py
│   │   ├── transcriber.py     # Speech-to-text (Whisper)
│   │   ├── processor.py       # Text processing & segmentation
│   │   ├── summarizer.py      # Summarization engine
│   │   └── note_generator.py  # Note formatting & export
│   ├── routes/                # API endpoints
│   │   ├── __init__.py
│   │   ├── upload.py          # File upload endpoint
│   │   ├── process.py         # Processing endpoint
│   │   └── export.py          # Export endpoint
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── helpers.py         # Helper functions
│   │   └── logger.py          # Logging setup
│   ├── main.py                # FastAPI app entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/                  # React/Vue frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── tests/                     # Test files
│   ├── test_transcriber.py
│   ├── test_processor.py
│   └── test_summarizer.py
├── docs/                      # Documentation
│   ├── SETUP.md              # Detailed setup guide
│   ├── API.md                # API documentation
│   ├── ARCHITECTURE.md       # System architecture
│   └── USAGE.md              # User guide
├── samples/                   # Sample files
│   ├── sample_lecture.mp3
│   └── sample_output.md
├── docker-compose.yml         # Docker setup (optional)
├── .gitignore
└── README.md                  # This file
```

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Speech-to-Text**: OpenAI Whisper or Vosk
- **Summarization**: Hugging Face Transformers (BART/T5)
- **NLP**: NLTK, spaCy
- **Document Export**: python-docx, fpdf2
- **Task Queue**: Celery + Redis (for async processing)
- **Database**: SQLite/PostgreSQL (for storing notes metadata)

### Frontend
- **Framework**: React.js or Vue.js
- **Styling**: Tailwind CSS
- **State Management**: Redux or Pinia
- **HTTP Client**: Axios
- **File Upload**: Dropzone.js

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx
- **Task Runner**: Celery
- **Message Broker**: Redis

---

## Features

### Phase 1: MVP (Minimum Viable Product) ✅ COMPLETE
- [x] Upload audio/video file
- [x] Extract transcript using Whisper
- [x] Generate basic summary
- [x] Export notes as Markdown/PDF
- [x] Simple web interface
- [x] Text processing & cleaning
- [x] Key phrase extraction
- [x] Keyword identification
- [x] Bullet point generation
- [x] Multiple export formats (PDF, Docx, Markdown)
- [x] RESTful API
- [x] Docker support
- [x] Unit tests

### Phase 2: Enhanced Features
- [ ] Speaker diarization (identify speakers)
- [ ] Slide detection & timestamps
- [ ] Keyword extraction
- [ ] Topic highlighting
- [ ] Search functionality

### Phase 3: Advanced Features
- [ ] Offline mode (local models)
- [ ] Multiple language support
- [ ] Custom summarization templates
- [ ] Glossary generation
- [ ] Interactive note editing
- [ ] User authentication & cloud storage

---

## 🚀 Quick Start (30 seconds)

### Windows
```bash
start.bat
```

### macOS/Linux
```bash
./start.sh
```

### Docker
```bash
docker-compose up --build
```

Then open: **http://localhost:5173**

---

## 📖 Detailed Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- FFmpeg (for audio processing)
- 4GB+ RAM
- GPU (optional, for faster processing)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend at: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend at: `http://localhost:5173`

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation
- **[Usage Guide](docs/USAGE.md)** - How to use the system
- **[API Reference](docs/API.md)** - Complete endpoint documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[Implementation Summary](IMPLEMENTATION_COMPLETE.md)** - What was built

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v                    # Run all tests
pytest tests/test_transcriber.py    # Run specific test
pytest tests/ --cov=modules         # With coverage report
```

---

## 🐳 Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

---

## 🌐 API Usage Examples

### Upload File
```bash
curl -X POST "http://localhost:8000/api/upload/" \
  -F "file=@lecture.mp3"
```

### Process File
```bash
curl -X POST "http://localhost:8000/api/process/" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"xxx","file_path":"./uploads/xxx_lecture.mp3","title":"Lecture"}'
```

### Export Notes
```bash
curl -X POST "http://localhost:8000/api/export/" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"xxx","format":"pdf","title":"Lecture"}'
```

See [docs/API.md](docs/API.md) for complete API reference.

---

## ⚙️ Configuration

### Backend (.env)
```env
WHISPER_MODEL=base      # tiny, base, small, medium, large
DEVICE=cpu              # cpu or cuda (for GPU)
DEBUG=True              # False in production
MAX_FILE_SIZE=500000000 # 500MB
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000/api
```

---

## 📊 Performance Metrics

| Task | Time |
|------|------|
| File Upload | < 1 second |
| Transcription | 1-5 minutes per hour |
| Text Processing | < 1 minute |
| Summarization | < 2 minutes |
| Note Export | < 5 seconds |

*Times vary based on file size, model, and hardware*

---

## 🔐 Security Features

- ✅ File size validation
- ✅ File type validation
- ✅ CORS configuration
- ✅ Error handling
- ✅ Input sanitization
- ✅ Comprehensive logging

---

## ✨ What's Included

- ✅ Complete backend (FastAPI + Python)
- ✅ Modern frontend (React + Vite)
- ✅ Docker support
- ✅ Unit tests
- ✅ Complete documentation
- ✅ Startup scripts for Windows/Unix
- ✅ Environment configuration
- ✅ API documentation with Swagger UI

---

## 📈 Project Status

**v1.0.0** - Initial Release ✅

All Phase 1 features implemented and tested:
- ✅ Transcription
- ✅ Text Processing
- ✅ Summarization
- ✅ Note Generation
- ✅ Multiple Export Formats
- ✅ REST API
- ✅ Web Interface
- ✅ Docker Deployment

---

## 🚀 Ready to Use!

This is a complete, production-ready system. Start processing lectures now!

**[Get Started →](docs/USAGE.md)**

For detailed setup, see [docs/SETUP.md](docs/SETUP.md)

---

## Usage

1. **Upload Lecture**: Go to the web app and upload an audio/video file
2. **Processing**: System transcribes and processes the lecture
3. **View Notes**: Review auto-generated notes in the UI
4. **Edit & Export**: Customize notes and export as PDF/Docx/Markdown

---

## API Endpoints (Backend)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload lecture file |
| GET | `/api/status/{job_id}` | Check processing status |
| GET | `/api/notes/{job_id}` | Retrieve generated notes |
| POST | `/api/export/{job_id}` | Export notes to format |
| DELETE | `/api/delete/{job_id}` | Delete job & notes |

For full API details, see [docs/API.md](docs/API.md)

---

## Development Milestones

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Planning** | Week 1-2 | Requirements, design, setup |
| **Phase 2: Backend MVP** | Week 3-5 | Transcription, processing, export |
| **Phase 3: Frontend MVP** | Week 6-7 | UI, upload, display |
| **Phase 4: Testing & Deployment** | Week 8-9 | Bug fixes, optimization, deployment |
| **Phase 5: Documentation & Report** | Week 10 | Final docs, report, presentation |

---

## Performance Metrics (Testing Goals)

- **Accuracy**: >90% transcript accuracy
- **Processing Time**: <5 min for 1-hour lecture (with GPU)
- **Summary Quality**: 70-80% of original content retained
- **API Response**: <2s for API calls
- **Storage**: <500MB for 1-hour lecture (transcript + notes)

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Background noise in lectures | Use audio preprocessing; multiple STT models |
| Large file processing | Implement async jobs with Celery |
| Summarization quality | Use fine-tuned models; human feedback loop |
| Scalability | Containerize with Docker; use load balancing |
| Privacy concerns | Encrypt uploads; auto-delete after processing |

---

## Future Enhancements

- Real-time live lecture notes generation
- Mobile app (React Native)
- Integration with Learning Management Systems (LMS)
- AI-powered Q&A from notes
- Multi-language support
- Custom model fine-tuning on domain-specific lectures

---

## Contributors
- **Developer**: Your Name
- **Supervisor**: College Name / Department

---

## License
MIT License - Open for educational use

---

## References & Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [React Documentation](https://react.dev/)

---

## Contact & Support
For issues or questions, open an issue in the project repository.

---

**Last Updated**: January 10, 2026  
**Status**: Development Phase
