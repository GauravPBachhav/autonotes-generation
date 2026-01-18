"""
API route for exporting notes in various formats
"""

import logging
import os
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.note_generator import NoteGenerator
from utils.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])


class ExportRequest(BaseModel):
    """Request model for exporting notes"""
    job_id: str
    format: str = "markdown"  # markdown, pdf, docx
    title: str = "Lecture Notes"


@router.post("/")
async def export_notes(request: ExportRequest):
    """
    Export processed notes in specified format
    
    Args:
        job_id: Processing job ID
        format: Export format (markdown, pdf, docx, all)
        title: Title for the exported document
        
    Returns:
        File path or all exported file paths
    """
    try:
        settings = get_settings()
        
        # Supported formats
        supported_formats = ["markdown", "pdf", "docx", "all"]
        if request.format not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {request.format}. Supported: {', '.join(supported_formats)}"
            )

        # Load transcript data
        transcript_path = os.path.join(settings.TEMP_DIR, f"{request.job_id}_transcript.json")
        if not os.path.exists(transcript_path):
            raise HTTPException(status_code=404, detail="Processing data not found. Process file first.")

        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = json.load(f)

        # Initialize note generator
        note_generator = NoteGenerator(output_dir=settings.OUTPUT_DIR)

        # Prepare note content (simplified for export)
        note_content = {
            "markdown": f"# {request.title}\n\n{transcript.get('text', '')}",
            "html": f"<h1>{request.title}</h1><p>{transcript.get('text', '')}</p>",
            "text": transcript.get("text", ""),
        }

        # Export based on format
        if request.format == "all":
            result = note_generator.export_all_formats(
                note_content,
                f"{request.job_id}_{request.title.replace(' ', '_')}",
                request.title,
            )
            return JSONResponse({
                "success": True,
                "job_id": request.job_id,
                "format": "all",
                "files": result,
            })

        elif request.format == "markdown":
            file_path = note_generator.export_markdown(
                note_content["markdown"],
                f"{request.job_id}_{request.title.replace(' ', '_')}",
            )
            return JSONResponse({
                "success": True,
                "job_id": request.job_id,
                "format": "markdown",
                "file_path": file_path,
                "file_url": f"/api/export/download/{request.job_id}/markdown",
            })

        elif request.format == "pdf":
            file_path = note_generator.export_pdf(
                note_content["markdown"],
                f"{request.job_id}_{request.title.replace(' ', '_')}",
                request.title,
            )
            return JSONResponse({
                "success": True,
                "job_id": request.job_id,
                "format": "pdf",
                "file_path": file_path,
                "file_url": f"/api/export/download/{request.job_id}/pdf",
            })

        elif request.format == "docx":
            file_path = note_generator.export_docx(
                note_content["markdown"],
                f"{request.job_id}_{request.title.replace(' ', '_')}",
                request.title,
            )
            return JSONResponse({
                "success": True,
                "job_id": request.job_id,
                "format": "docx",
                "file_path": file_path,
                "file_url": f"/api/export/download/{request.job_id}/docx",
            })

    except HTTPException as e:
        logger.error(f"Export error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/download/{job_id}/{format}")
async def download_file(job_id: str, format: str):
    """Download exported file"""
    try:
        settings = get_settings()
        
        # Find file with job_id prefix
        format_ext = {"markdown": ".md", "pdf": ".pdf", "docx": ".docx"}
        if format not in format_ext:
            raise HTTPException(status_code=400, detail="Invalid format")

        for filename in os.listdir(settings.OUTPUT_DIR):
            if filename.startswith(job_id) and filename.endswith(format_ext[format]):
                file_path = os.path.join(settings.OUTPUT_DIR, filename)
                return FileResponse(
                    file_path,
                    media_type="application/octet-stream",
                    filename=filename,
                )

        raise HTTPException(status_code=404, detail="File not found")

    except HTTPException as e:
        logger.error(f"Download error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
