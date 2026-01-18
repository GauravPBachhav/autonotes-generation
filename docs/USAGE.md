# Quick Start Guide - Autonotes Generation

## System Requirements
- **OS**: Windows, macOS, Linux
- **Python**: 3.9+
- **Node.js**: 16+
- **RAM**: 4GB minimum (8GB+ recommended for faster processing)
- **Storage**: 10GB+ for models and output

---

## Installation

### Option 1: Local Development Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create environment file
copy .env.example .env
# Edit .env if needed (default values work for local development)

# Create necessary directories
mkdir uploads temp output logs

# Start backend server
python main.py
```

Backend will run at: `http://localhost:8000`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file (already included: .env.local)

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

---

### Option 2: Docker Setup

```bash
# Navigate to project root
cd autonotes-generation

# Build and run with Docker Compose
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

Access:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## First Run

### 1. Access the Application
Open browser and go to: `http://localhost:5173`

You should see the Autonotes Generation interface.

### 2. Upload a File
- Click "Browse Files" or drag-drop an audio/video file
- Supported formats: MP3, WAV, MP4, AVI, MOV, MKV
- Maximum file size: 500MB

### 3. Wait for Processing
The system will:
1. Transcribe audio using Whisper AI
2. Process and clean the transcript
3. Generate summary and key points
4. Extract keywords

Processing time depends on:
- File duration (usually 1-5 minutes per hour of audio)
- Your computer's CPU/GPU
- Selected Whisper model size

### 4. View Results
Once complete, you'll see:
- **Summary**: Key takeaways
- **Key Points**: Bullet points from the lecture
- **Keywords**: Important terms mentioned
- **Full Transcript**: Complete transcription

### 5. Export Notes
Export your notes in:
- 📝 **Markdown**: Plain text format for easy editing
- 📄 **PDF**: Professional document format
- 📋 **Word**: Microsoft Word format (.docx)
- 📦 **All**: Download all three formats

---

## Configuration

### Backend Configuration (.env)

Key settings in `backend/.env`:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# File sizes (in bytes)
MAX_FILE_SIZE=500000000  # 500MB

# Whisper model size
WHISPER_MODEL=base  # tiny, base, small, medium, large
# - tiny: Fastest, less accurate (10 seconds per minute of audio)
# - base: Balanced (15 seconds per minute)
# - small: Better accuracy (30 seconds per minute)
# - medium: High quality (1-2 minutes per minute)
# - large: Best quality (3-5 minutes per minute)

# Processing device
DEVICE=cpu  # Use 'cuda' if you have NVIDIA GPU

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/autonotes.log
```

### Frontend Configuration (.env.local)

```env
VITE_API_URL=http://localhost:8000/api
```

---

## Project Structure

```
autonotes-generation/
├── backend/
│   ├── modules/
│   │   ├── transcriber.py     # Audio → Text
│   │   ├── processor.py       # Text cleaning & segmentation
│   │   ├── summarizer.py      # Text summarization
│   │   └── note_generator.py  # Export to PDF/Docx/Markdown
│   ├── routes/
│   │   ├── upload.py          # File upload API
│   │   ├── process.py         # Processing pipeline API
│   │   └── export.py          # Export API
│   ├── utils/
│   │   ├── config.py          # Configuration
│   │   ├── helpers.py         # Utility functions
│   │   └── logger.py          # Logging setup
│   ├── main.py                # FastAPI app
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ProcessingStatus.jsx
│   │   │   └── NoteViewer.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── tests/
│   ├── test_transcriber.py
│   ├── test_processor.py
│   └── test_summarizer.py
├── docs/
│   ├── SETUP.md              # Setup guide
│   ├── API.md                # API documentation
│   ├── ARCHITECTURE.md       # System architecture
│   └── USAGE.md              # User guide
└── docker-compose.yml        # Docker configuration
```

---

## Running Tests

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_transcriber.py -v

# Run with coverage
pytest tests/ --cov=modules --cov=routes --cov=utils
```

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Make sure spaCy model is installed
python -m spacy download en_core_web_sm
```

### Issue: Port already in use
**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Or change port in .env
PORT=8001
```

### Issue: Out of memory during processing
**Solution:**
- Use smaller Whisper model: `WHISPER_MODEL=tiny`
- Increase available RAM
- Process shorter files

### Issue: GPU not detected
**Solution:**
```bash
# Check CUDA installation
nvcc --version

# Install GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update .env
DEVICE=cuda
```

### Issue: Frontend can't connect to backend
**Solution:**
1. Verify backend is running: `http://localhost:8000/health`
2. Check frontend .env.local has correct API URL
3. Check CORS settings in backend .env

---

## Building for Production

### Backend Build
```bash
# Build Docker image
docker build -t autonotes-backend:latest ./backend

# Run container
docker run -p 8000:8000 \
  -e DEVICE=cpu \
  -e WHISPER_MODEL=base \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/output:/app/output \
  autonotes-backend:latest
```

### Frontend Build
```bash
# Create optimized build
npm run build

# Output in 'dist' directory
# Deploy to web server (Nginx, Apache, etc.)
```

### Docker Compose Production
```bash
# Build all services
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Performance Tips

1. **Use GPU**: If you have NVIDIA GPU, set `DEVICE=cuda` for 10x faster processing
2. **Smaller Model**: Use `WHISPER_MODEL=tiny` or `base` for faster transcription
3. **Batch Processing**: Process multiple files in sequence, not parallel
4. **Disk Space**: Ensure 10+ GB free disk space for models and outputs
5. **Memory**: Close other applications during processing

---

## Support & Documentation

- **API Docs**: Visit `http://localhost:8000/docs`
- **Architecture**: See [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **API Reference**: See [docs/API.md](API.md)
- **Issues**: Check GitHub or project documentation

---

## Next Steps

1. ✅ **Install & Run**: Get the system running locally
2. 📚 **Process Sample**: Try with your first lecture
3. 🎨 **Customize**: Modify models and settings as needed
4. 🚀 **Deploy**: Move to production with Docker
5. 🔧 **Integrate**: Use APIs in your own applications

---

## Licensing & Credits

Autonotes Generation uses:
- **Whisper**: OpenAI's speech recognition model
- **Transformers**: Hugging Face BART/T5 for summarization
- **spaCy**: NLP processing
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework

---

Happy note-taking! 🎓
