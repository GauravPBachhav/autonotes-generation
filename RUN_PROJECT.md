# 🚀 How to Run the Project

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Open the App

Open your browser at: **http://localhost:5173**

---

## Detailed Instructions

### Backend Setup (Python 3.8+)

1. **Navigate to backend folder:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn python-multipart pydub SpeechRecognition python-docx fpdf2 markdown pydantic-settings aiofiles
   ```
   
   Or use requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server:**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Backend will run at: **http://localhost:8000**

### Frontend Setup (Node.js 16+)

1. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will run at: **http://localhost:5173**

---

## Using the App

1. **Upload Audio**: Click "Choose File" and select an audio file (MP3, WAV, M4A, etc.)
2. **Process**: Click "Upload & Process" button
3. **View Notes**: Switch between:
   - 🎙️ **Original Transcription** tab - raw word-by-word transcript
   - 📝 **Structured Notes** tab - organized topics, takeaways, definitions, keywords
4. **Export**: Click buttons to download as Markdown, PDF, or DOCX

---

## Troubleshooting

### Backend won't start?
- Check Python version: `python --version` (need 3.8+)
- Install missing packages: `pip install -r backend/requirements.txt`
- Port already in use? Change port: `python -m uvicorn main:app --port 8001`

### Frontend won't start?
- Check Node version: `node --version` (need 16+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Port already in use? Change in `vite.config.js` or use: `npx vite --port 5174`

### "Connection refused" errors?
- Make sure backend is running on port 8000
- Check CORS settings in `backend/main.py`

---

## Project Structure

```
autonotes-generation/
├── backend/              # Python FastAPI backend
│   ├── main.py          # Entry point
│   ├── modules/         # Core processing modules
│   ├── routes/          # API endpoints
│   └── utils/           # Config & helpers
├── frontend/            # React + Vite frontend
│   └── src/
│       ├── App.jsx      # Main app component
│       └── components/  # UI components
└── tests/               # Test files
```

---

## Features

✅ **Audio Transcription** - Converts speech to text  
✅ **Smart Processing** - Detects topics, definitions, key takeaways  
✅ **Two-Section Output** - Original transcript + Structured notes  
✅ **Multi-Format Export** - Markdown, PDF, DOCX  
✅ **Beautiful UI** - Modern card-based design with tabs  

---

## Tech Stack

- **Backend**: FastAPI, Python 3.13, SpeechRecognition, FPDF2
- **Frontend**: React 18, Vite, Axios
- **Processing**: Custom NLP (no ML models - pure Python)

---

**Need help?** Check the logs:
- Backend logs: `backend/logs/autonotes.log`
- Frontend console: Press F12 in browser
