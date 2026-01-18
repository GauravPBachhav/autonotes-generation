"""
API route for file upload
"""

import logging
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import aiofiles

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import get_settings
from utils.helpers import (
    generate_job_id,
    get_file_extension,
    validate_file_extension,
    format_file_size,
    get_file_size,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Supported file formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4", ".avi", ".mov", ".mkv"}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload audio or video file for processing
    
    Returns:
        job_id: Unique identifier for this processing job
        filename: Original filename
        file_size: Size of uploaded file
    """
    try:
        settings = get_settings()
        
        # Validate file format
        file_ext = get_file_extension(file.filename)
        if file_ext not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(SUPPORTED_FORMATS)}"
            )

        # Create upload directory
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Generate unique job ID
        job_id = generate_job_id()
        
        # Save file with job ID as prefix
        filename = f"{job_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        # Save uploaded file
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds limit: {format_file_size(len(content))} > {format_file_size(settings.MAX_FILE_SIZE)}"
                )
            
            await f.write(content)

        file_size = get_file_size(file_path)
        logger.info(f"File uploaded successfully - Job: {job_id}, Size: {format_file_size(file_size)}")
        logger.info(f"Uploaded file_path: {file_path}, File exists: {os.path.exists(file_path)}")

        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_size_formatted": format_file_size(file_size),
        })

    except HTTPException as e:
        logger.error(f"Upload validation error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/status/{job_id}")
async def check_upload_status(job_id: str):
    """Check if uploaded file exists"""
    try:
        settings = get_settings()
        
        # Look for file with job_id prefix
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.startswith(job_id):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                file_size = get_file_size(file_path)
                logger.info(f"Status check - Job: {job_id}, Path: {file_path}, Exists: {os.path.exists(file_path)}")
                
                return JSONResponse({
                    "success": True,
                    "job_id": job_id,
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": file_size,
                    "exists": True,
                })
        
        return JSONResponse({
            "success": False,
            "job_id": job_id,
            "exists": False,
            "message": "File not found",
        })

    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
