"""
API route for processing audio/video and generating notes
"""

import logging
import os
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.transcriber import Transcriber
from modules.processor import TextProcessor
from modules.summarizer import Summarizer
from modules.note_generator import NoteGenerator
from utils.config import get_settings
from utils.helpers import get_filename_without_extension

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/process", tags=["process"])


class ProcessRequest(BaseModel):
    """Request model for processing"""
    job_id: str
    file_path: str
    language: str = None
    title: str = "Lecture Notes"


class ProcessResponse(BaseModel):
    """Response model for processing"""
    success: bool
    job_id: str
    status: str
    transcript: dict = None
    processed_data: dict = None
    summaries: dict = None
    error: str = None


@router.post("/")
async def process_file(request: ProcessRequest):
    """
    Process uploaded file: transcribe, process, and summarize
    
    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded file
        language: Language code (optional)
        title: Lecture title
        
    Returns:
        Processing results with transcript, processed data, and summaries
    """
    try:
        settings = get_settings()
        logger.info(f"Processing started - Job: {request.job_id}")
        logger.info(f"File path received: {request.file_path}")
        logger.info(f"Checking if file exists at: {request.file_path}")

        # Verify file exists
        if not os.path.exists(request.file_path):
            logger.error(f"File not found at: {request.file_path}")
            logger.error(f"Upload dir exists: {os.path.exists(settings.UPLOAD_DIR)}")
            logger.error(f"Upload dir contents: {os.listdir(settings.UPLOAD_DIR) if os.path.exists(settings.UPLOAD_DIR) else 'N/A'}")
            raise HTTPException(status_code=404, detail=f"File not found at {request.file_path}")

        # Initialize processing modules
        transcriber = Transcriber(
            model_name=settings.WHISPER_MODEL,
            device=settings.DEVICE,
        )
        processor = TextProcessor()
        summarizer = Summarizer(
            model_name=settings.SUMMARIZATION_MODEL,
            device=settings.DEVICE,
        )
        note_generator = NoteGenerator(output_dir=settings.OUTPUT_DIR)

        # Step 1: Transcription
        logger.info("Step 1: Transcribing audio...")
        transcript = transcriber.transcribe(request.file_path, language=request.language)
        logger.info(f"Transcription complete: {transcript['duration']}s, {len(transcript['text'].split())} words")

        # Step 2: Text Processing
        logger.info("Step 2: Processing text...")
        combined_text = transcriber.combine_segments(transcript["segments"])
        processed_data = processor.process_transcript(combined_text)
        logger.info(f"Processing complete: {processed_data['section_count']} sections")

        # Step 3: Summarization
        logger.info("Step 3: Generating summary...")
        overall_summary = summarizer.summarize(
            processed_data["cleaned_text"],
            min_length=settings.MIN_SUMMARY_LENGTH,
            max_length=settings.MAX_SUMMARY_LENGTH,
        )
        
        section_summaries = summarizer.summarize_sections(
            processed_data["sections"],
            min_length=50,
            max_length=150,
        )
        
        bullet_points = summarizer.extract_bullet_points(
            processed_data["cleaned_text"],
            num_points=10,
        )
        
        processed_data["sections"] = section_summaries
        
        summaries = {
            "overall_summary": overall_summary,
            "bullet_points": bullet_points,
        }
        
        logger.info(f"Summarization complete: {len(bullet_points)} bullet points")

        # Step 4: Generate Notes (optional)
        logger.info("Step 4: Generating formatted notes...")
        note_content = note_generator.generate_note_content(
            title=request.title,
            transcript_data=transcript,
            processed_data=processed_data,
            summaries=summaries,
        )

        # Save transcript and data
        transcript_path = os.path.join(
            settings.TEMP_DIR,
            f"{request.job_id}_transcript.json"
        )
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)

        logger.info(f"Processing completed successfully - Job: {request.job_id}")

        # Build structured notes data for frontend
        structured_notes = processed_data.get("structured_notes", {})

        return JSONResponse({
            "success": True,
            "job_id": request.job_id,
            "status": "completed",
            "transcript": {
                "text": transcript["text"],
                "duration": transcript["duration"],
                "language": transcript["language"],
                "segment_count": len(transcript["segments"]),
            },
            "processed_data": {
                "section_count": processed_data["section_count"],
                "word_count": processed_data["word_count"],
                "sentence_count": processed_data["sentence_count"],
                "keywords": processed_data["keywords"],
                "key_phrases": processed_data.get("key_phrases", []),
                "sections": [
                    {
                        "title": s.get("title", f"Topic {i+1}"),
                        "text": s.get("text", ""),
                        "keywords": s.get("keywords", []),
                        "summary": s.get("summary", ""),
                    }
                    for i, s in enumerate(processed_data.get("sections", []))
                ],
            },
            "structured_notes": {
                "topics": structured_notes.get("topics", []),
                "definitions": structured_notes.get("definitions", []),
                "key_takeaways": structured_notes.get("key_takeaways", []),
                "quick_revision": structured_notes.get("quick_revision", []),
            },
            "summaries": {
                "overall_summary": summaries["overall_summary"],
                "bullet_point_count": len(summaries["bullet_points"]),
                "bullet_points": summaries["bullet_points"],
            },
        })

    except HTTPException as e:
        logger.error(f"Processing error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Processing failed - Job: {request.job_id} - Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/status/{job_id}")
async def check_process_status(job_id: str):
    """Check processing status"""
    try:
        settings = get_settings()
        transcript_path = os.path.join(settings.TEMP_DIR, f"{job_id}_transcript.json")
        
        if os.path.exists(transcript_path):
            return JSONResponse({
                "success": True,
                "job_id": job_id,
                "status": "completed",
                "transcript_available": True,
            })
        
        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "transcript_available": False,
        })

    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
