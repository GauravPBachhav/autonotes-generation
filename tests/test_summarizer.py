"""
Test module for Summarizer
"""

import pytest
from backend.modules.summarizer import Summarizer


@pytest.fixture
def summarizer():
    """Create summarizer instance"""
    return Summarizer(model_name="simple", device="cpu")


def test_summarizer_initialization():
    """Test summarizer initialization"""
    summarizer = Summarizer(device="cpu")
    assert summarizer.model_name == "simple"


def test_summarize(summarizer):
    """Test text summarization"""
    text = "This is a long text that needs summarization. It contains important information about the topic. " * 10
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
    text = "Word " * 2000
    chunks = summarizer._split_into_chunks(text, max_chunk_size=100)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.split()) <= 120


def test_summarize_sections(summarizer):
    """Test section summarization"""
    sections = [
        {"text": "This is section one with some content. " * 5},
        {"text": "This is section two with more content. " * 5},
    ]

    result = summarizer.summarize_sections(sections)

    assert len(result) == 2
    assert all("summary" in section for section in result)


def test_extract_bullet_points(summarizer):
    """Test bullet point extraction"""
    text = (
        "Machine learning is a subset of artificial intelligence that enables systems to learn. "
        "Deep learning uses neural networks with many layers for complex pattern recognition. "
        "Supervised learning requires labeled training data to make predictions. "
        "Unsupervised learning finds hidden patterns in data without explicit labels. "
        "Reinforcement learning involves an agent learning through trial and error interactions."
    )

    points = summarizer.extract_bullet_points(text, num_points=3)

    assert isinstance(points, list)
    assert len(points) <= 3
    assert all(isinstance(p, str) for p in points)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
