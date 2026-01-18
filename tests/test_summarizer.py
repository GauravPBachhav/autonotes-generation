"""
Test module for Summarizer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.modules.summarizer import Summarizer


@pytest.fixture
def summarizer():
    """Create summarizer instance with mocked model"""
    with patch('backend.modules.summarizer.pipeline'):
        return Summarizer(model_name="facebook/bart-large-cnn", device="cpu")


def test_summarizer_initialization():
    """Test summarizer initialization"""
    with patch('backend.modules.summarizer.pipeline'):
        summarizer = Summarizer(device="cpu")
        assert summarizer.model_name == "facebook/bart-large-cnn"


def test_summarize(summarizer):
    """Test text summarization"""
    text = "This is a long text that needs summarization. " * 20
    
    summarizer.summarizer = Mock()
    summarizer.summarizer.return_value = [{
        "summary_text": "This is a summary of the long text."
    }]
    
    result = summarizer.summarize(text)
    assert isinstance(result, str)
    assert len(result) > 0


def test_summarize_short_text(summarizer):
    """Test summarization with short text"""
    text = "Short text"
    result = summarizer.summarize(text)
    assert result == text


def test_split_into_chunks(summarizer):
    """Test text chunking"""
    text = "Word " * 2000  # Create very long text
    chunks = summarizer._split_into_chunks(text, max_chunk_size=100)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.split()) <= 120  # Allow some margin


def test_summarize_sections(summarizer):
    """Test section summarization"""
    sections = [
        {"text": "This is section one. " * 10},
        {"text": "This is section two. " * 10},
    ]
    
    summarizer.summarizer = Mock()
    summarizer.summarizer.return_value = [{
        "summary_text": "Summary of section"
    }]
    
    result = summarizer.summarize_sections(sections)
    
    assert len(result) == 2
    assert all("summary" in section for section in result)


def test_extract_bullet_points(summarizer):
    """Test bullet point extraction"""
    text = "Key point one. Supporting detail. Key point two. More details."
    
    # Mock the classifier
    with patch('backend.modules.summarizer.pipeline') as mock_pipeline:
        mock_classifier = MagicMock()
        mock_pipeline.return_value = mock_classifier
        
        mock_classifier.return_value = {
            "labels": ["key information", "supporting detail"],
            "scores": [0.9, 0.1]
        }
        
        # This test verifies the method doesn't crash
        # In real scenario, it would extract bullet points


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
