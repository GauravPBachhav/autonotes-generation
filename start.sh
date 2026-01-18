#!/bin/bash
# Autonotes Generation - Start Script (macOS/Linux)

echo "🎓 Autonotes Generation - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo "✅ Node.js version: $(node --version)"
echo ""

# Start Backend
echo "🚀 Starting Backend Server..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if ! pip show fastapi > /dev/null; then
    echo "   Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
mkdir -p uploads temp output logs

# Start backend in background
python main.py &
BACKEND_PID=$!
echo "   Backend started (PID: $BACKEND_PID)"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Wait for backend to start
sleep 3

# Start Frontend
echo "🚀 Starting Frontend Server..."
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "   Installing Node dependencies..."
    npm install
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend started (PID: $FRONTEND_PID)"
echo "   App: http://localhost:5173"
echo ""

echo "======================================"
echo "✨ All services started successfully!"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
