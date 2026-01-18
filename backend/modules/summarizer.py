"""
Summarization Module
Simple version - generates summaries from key sentences
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class Summarizer:
    """Generate summaries using simple extraction"""

    def __init__(self, model_name: str = "simple", device: str = "cpu"):
        """
        Initialize Summarizer with simple extractive model
        """
        self.model_name = model_name
        self.device = device
        logger.info("Summarizer initialized (simple mode)")

    def summarize(self, text: str, min_length: int = 100, max_length: int = 500) -> str:
        """
        Summarize text using extractive method
        """
        try:
            if len(text.split()) < 50:
                logger.warning("Text too short to summarize")
                return text

            logger.info(f"Summarizing text (length: {len(text.split())} words)")
            
            # Simple extractive summarization
            sentences = text.split('. ')
            if not sentences:
                return text
            
            # Select every nth sentence to create summary
            summary_sentences = sentences[::max(1, len(sentences) // 3)]
            summary = '. '.join(summary_sentences)
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            logger.info(f"Summarization complete. Original: {len(text.split())} words, Summary: {len(summary.split())} words")
            return summary

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return text

    def summarize_sections(self, sections: List[Dict[str, str]], min_length: int = 50, max_length: int = 150) -> List[Dict]:
        """
        Summarize individual sections
        """
        summarized = []
        
        for i, section in enumerate(sections):
            try:
                text = section.get("text", "")
                
                if len(text.split()) < 20:
                    summary = text
                else:
                    summary = self.summarize(text, min_length, max_length)
                
                section_with_summary = section.copy()
                section_with_summary["summary"] = summary
                summarized.append(section_with_summary)
                
                logger.debug(f"Section {i+1}/{len(sections)} summarized")
                
            except Exception as e:
                logger.warning(f"Failed to summarize section {i+1}: {e}")
                section["summary"] = section.get("text", "")
                summarized.append(section)

        logger.info(f"Summarized {len(summarized)} sections")
        return summarized

    def extract_bullet_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key bullet points from text
        """
        try:
            # Split into sentences
            sentences = text.split('. ')
            
            # Filter longer sentences (likely to contain more information)
            scored = [(s.strip(), len(s.split())) for s in sentences if len(s.split()) > 10]
            
            # Sort by length (longer = more informative)
            scored.sort(key=lambda x: x[1], reverse=True)
            
            # Return top points
            bullet_points = [s[0] + "." if not s[0].endswith('.') else s[0] for s in scored[:num_points]]
            
            logger.info(f"Extracted {len(bullet_points)} bullet points")
            return bullet_points
            
        except Exception as e:
            logger.warning(f"Bullet point extraction failed: {e}")
            return []

    def _split_into_chunks(self, text: str, max_chunk_size: int = 1024) -> List[str]:
        """Split text into chunks based on size"""
        sentences = text.split(". ")
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size > max_chunk_size and current_chunk:
                chunks.append(". ".join(current_chunk) + ".")
                current_chunk = []
                current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size

        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")

        return chunks
