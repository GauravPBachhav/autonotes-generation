"""
FastAPI main application entry point
Autonotes Generation - Automatic note generation from lectures
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import get_settings
from utils.logger import setup_logging
from routes import upload_router, process_router, export_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Autonotes Generation API",
    description="Automatically generate structured notes from lecture recordings",
    version="1.0.0",
)

# Get settings
settings = get_settings()

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (can be restricted later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "autonotes-generation",
        "version": "1.0.0",
    })


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return JSONResponse({
        "message": "Autonotes Generation API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "process": "/api/process",
            "export": "/api/export",
            "docs": "/docs",
        },
    })


# API Status endpoint
@app.get("/api/status")
async def api_status():
    """Get API status and configuration"""
    return JSONResponse({
        "status": "running",
        "debug": settings.DEBUG,
        "max_file_size": settings.MAX_FILE_SIZE,
        "whisper_model": settings.WHISPER_MODEL,
        "device": settings.DEVICE,
    })


# Register routers
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(export_router)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Endpoint not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    import os
    
    logger.info("Starting Autonotes Generation API")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Whisper Model: {settings.WHISPER_MODEL}")
    logger.info(f"Device: {settings.DEVICE}")
    logger.info(f"Upload Directory: {settings.UPLOAD_DIR}")
    logger.info(f"Output Directory: {settings.OUTPUT_DIR}")
    
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    logger.info("Directories created/verified")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Autonotes Generation API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
