"""
Test module for Transcriber
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from backend.modules.transcriber import Transcriber


@pytest.fixture
def transcriber():
    """Create transcriber instance with mocked model"""
    with patch('backend.modules.transcriber.whisper.load_model'):
        return Transcriber(model_name="base", device="cpu")


def test_transcriber_initialization():
    """Test transcriber initialization"""
    with patch('backend.modules.transcriber.whisper.load_model'):
        transcriber = Transcriber(model_name="small", device="cpu")
        assert transcriber.model_name == "small"
        assert transcriber.device == "cpu"


def test_extract_audio_with_audio_file(transcriber):
    """Test audio extraction with audio file"""
    result = transcriber.extract_audio("test.mp3")
    assert result == "test.mp3"


def test_extract_audio_with_video_file(transcriber):
    """Test audio extraction with video file"""
    with patch('backend.modules.transcriber.AudioSegment.from_file') as mock_audio:
        mock_audio_instance = MagicMock()
        mock_audio.return_value = mock_audio_instance
        mock_audio_instance.export = MagicMock()
        
        result = transcriber.extract_audio("test.mp4")
        assert result.endswith(".mp3")


def test_transcribe(transcriber):
    """Test transcription"""
    mock_result = {
        "text": "This is a test transcript",
        "segments": [
            {"id": 1, "start": 0.0, "end": 5.0, "text": "This is a test"},
            {"id": 2, "start": 5.0, "end": 10.0, "text": "transcript"}
        ],
        "language": "en",
        "duration": 10.0,
    }
    
    transcriber.model.transcribe = Mock(return_value=mock_result)
    
    with patch.object(transcriber, 'extract_audio', return_value="test.mp3"):
        result = transcriber.transcribe("test.mp4")
        
        assert result["text"] == "This is a test transcript"
        assert result["language"] == "en"
        assert len(result["segments"]) == 2


def test_format_segments(transcriber):
    """Test segment formatting"""
    segments = [
        {"id": 1, "start": 0.0, "end": 5.5, "text": "Hello world"},
        {"id": 2, "start": 5.5, "end": 10.123, "text": "Test segment"}
    ]
    
    formatted = transcriber._format_segments(segments)
    
    assert formatted[0]["start"] == 0.0
    assert formatted[0]["end"] == 5.5
    assert formatted[1]["end"] == 10.12  # Rounded to 2 decimals


def test_save_transcript(transcriber, tmp_path):
    """Test saving transcript"""
    transcript = {
        "text": "Test transcript",
        "segments": [],
        "language": "en",
        "duration": 10.0,
    }
    
    output_path = tmp_path / "test_transcript.json"
    transcriber.save_transcript(transcript, str(output_path))
    
    assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
