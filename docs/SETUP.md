# Setup Guide - Autonotes Generation

## Prerequisites Checklist
- [ ] Python 3.9 or higher installed
- [ ] Node.js 16+ installed
- [ ] Git installed
- [ ] FFmpeg installed (`pip install ffmpeg-python` or system package)
- [ ] 4GB+ RAM available
- [ ] Text editor/IDE (VS Code recommended)

---

## Backend Setup (Python/FastAPI)

### Step 1: Create Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create Environment File
```bash
copy .env.example .env
# Edit .env with your configuration
```

### Step 4: Run Backend Server
```bash
python main.py
```
Backend runs at `http://localhost:8000`

---

## Frontend Setup (React)

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Configure Backend URL
Edit `.env.local`:
```
VITE_API_URL=http://localhost:8000/api
```

### Step 3: Run Frontend Dev Server
```bash
npm run dev
```
Frontend runs at `http://localhost:5173`

---

## Docker Setup (Optional)

### Build & Run with Docker Compose
```bash
docker-compose up -d
```

---

## Verification

### Test Backend
```bash
curl http://localhost:8000/health
```

### Test Frontend
Open `http://localhost:5173` in browser

---

## Troubleshooting

- **Import errors**: Reinstall requirements
- **Port already in use**: Change ports in config
- **FFmpeg missing**: Install from system package manager
- **Out of memory**: Reduce batch size in config

---

## Next Steps
- Review [API.md](API.md) for endpoint documentation
- Check [USAGE.md](USAGE.md) for usage examples
