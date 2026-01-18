"""
Test module for TextProcessor
"""

import pytest
from backend.modules.processor import TextProcessor


@pytest.fixture
def processor():
    """Create processor instance"""
    return TextProcessor()


def test_processor_initialization():
    """Test processor initialization"""
    processor = TextProcessor()
    assert processor.stop_words is not None


def test_clean_text(processor):
    """Test text cleaning"""
    text = "Um, this is like, a test   transcript with, er, filler words"
    cleaned = processor.clean_text(text)
    
    assert "Um" not in cleaned
    assert "like" not in cleaned
    assert "er" not in cleaned
    assert "test" in cleaned
    assert "transcript" in cleaned


def test_clean_text_brackets(processor):
    """Test cleaning bracketed text"""
    text = "This is [inaudible] some text [background noise] end"
    cleaned = processor.clean_text(text)
    
    assert "[inaudible]" not in cleaned
    assert "[background noise]" not in cleaned
    assert "This is" in cleaned
    assert "some text" in cleaned


def test_segment_by_sentences(processor):
    """Test sentence segmentation"""
    text = "This is sentence one. This is sentence two. And here is sentence three."
    segments = processor.segment_by_sentences(text)
    
    assert len(segments) == 3
    assert "sentence one" in segments[0]
    assert "sentence two" in segments[1]


def test_segment_by_sections(processor):
    """Test section segmentation"""
    text = "First section. " * 40 + "Second section. " * 40
    sections = processor.segment_by_sections(text, max_section_length=200)
    
    assert len(sections) >= 2
    assert all("text" in section for section in sections)
    assert all("length" in section for section in sections)


def test_extract_key_phrases(processor):
    """Test key phrase extraction"""
    text = "Machine Learning is a subset of Artificial Intelligence. Deep Learning uses neural networks."
    phrases = processor.extract_key_phrases(text, top_n=5)
    
    assert isinstance(phrases, list)
    assert len(phrases) <= 5


def test_extract_keywords(processor):
    """Test keyword extraction"""
    text = "Python is a programming language. Python is used for machine learning. Python is versatile."
    keywords = processor.extract_keywords(text, top_n=5)
    
    assert isinstance(keywords, list)
    assert len(keywords) <= 5
    assert "python" in [kw.lower() for kw in keywords]


def test_process_transcript(processor):
    """Test full transcript processing"""
    text = "This is a test transcript. It contains multiple sentences. And some important concepts."
    
    result = processor.process_transcript(text)
    
    assert "original_text" in result
    assert "cleaned_text" in result
    assert "sections" in result
    assert "key_phrases" in result
    assert "keywords" in result
    assert result["section_count"] > 0
    assert result["word_count"] > 0


def test_combine_segments(processor):
    """Test combining segments"""
    segments = [
        {"text": "First part"},
        {"text": "Second part"},
        {"text": "Third part"},
    ]
    
    combined = processor.combine_segments(segments)
    assert "First part" in combined
    assert "Second part" in combined
    assert "Third part" in combined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
