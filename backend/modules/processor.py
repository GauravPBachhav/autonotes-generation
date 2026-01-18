"""
Text Processing Module
Cleans, segments, and extracts key information from transcripts
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Basic stop words (simplified)
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that', 'the',
    'to', 'was', 'will', 'with'
}


class TextProcessor:
    """Process and structure raw transcripts"""

    def __init__(self):
        """Initialize processor"""
        self.stop_words = STOP_WORDS
        self.nlp = None

    def clean_text(self, text: str) -> str:
        """
        Clean transcript text
        - Remove extra whitespace
        - Remove common filler words
        - Fix punctuation
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove filler words
        filler_patterns = [
            r'\b(um|uh|ah|er|erm|like|basically|you know|i mean)\b',
            r'\[.*?\]',  # Remove bracketed text like [inaudible]
            r'\(.*?\)',  # Remove parenthetical asides
        ]
        
        for pattern in filler_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def segment_by_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple split)"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def segment_by_sections(self, text: str, max_section_length: int = 500) -> List[Dict[str, str]]:
        """
        Segment text into logical sections
        Groups related sentences together based on length and content breaks
        """
        sentences = self.segment_by_sentences(text)
        sections = []
        current_section = []
        current_length = 0

        for sentence in sentences:
            sent_length = len(sentence)
            
            # Start new section if current exceeds max length
            if current_length + sent_length > max_section_length and current_section:
                sections.append({
                    "text": " ".join(current_section),
                    "length": current_length,
                    "sentence_count": len(current_section),
                })
                current_section = []
                current_length = 0
            
            current_section.append(sentence)
            current_length += sent_length

        # Add last section
        if current_section:
            sections.append({
                "text": " ".join(current_section),
                "length": current_length,
                "sentence_count": len(current_section),
            })

        return sections

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key phrases (simple version - just frequent multi-word phrases)
        """
        # Just return top keywords as "phrases"
        return self.extract_keywords(text, top_n)

    def extract_keywords(self, text: str, top_n: int = 15) -> List[str]:
        """
        Extract important keywords using simple frequency
        """
        # Simple word tokenization
        words = text.lower().split()
        
        # Filter out stop words and non-alphanumeric
        keywords = [
            w for w in words
            if w.isalnum() and w not in self.stop_words and len(w) > 2
        ]
        
        # Count frequency
        freq = {}
        for word in keywords:
            freq[word] = freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_keywords[:top_n]]

    def process_transcript(self, text: str) -> Dict:
        """
        Full processing pipeline
        
        Returns:
            Processed transcript with cleaning, segmentation, and extraction
        """
        logger.info("Starting text processing")
        
        cleaned_text = self.clean_text(text)
        sections = self.segment_by_sections(cleaned_text)
        key_phrases = self.extract_key_phrases(cleaned_text)
        keywords = self.extract_keywords(cleaned_text)
        
        # Generate simplified notes from cleaned text
        simplified_notes = self._generate_simplified_notes(cleaned_text, sections)

        processed = {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "simplified_notes": simplified_notes,
            "sections": sections,
            "section_count": len(sections),
            "key_phrases": key_phrases,
            "keywords": keywords,
            "word_count": len(cleaned_text.split()),
            "sentence_count": len(self.segment_by_sentences(cleaned_text)),
        }

        logger.info(f"Processing complete. Sections: {len(sections)}, Words: {processed['word_count']}")
        return processed

    def _generate_simplified_notes(self, text: str, sections: List[Dict]) -> str:
        """
        Generate simplified, well-organized notes from transcript
        with better structure and explanations
        """
        lines = []
        
        # Group sentences into logical chunks
        sentences = self.segment_by_sentences(text)
        
        if len(sentences) > 0:
            lines.append("## Key Topics and Explanations\n")
            
            # Group every 3-4 sentences into a concept
            chunk_size = max(2, len(sentences) // 5)  # Create ~5 chunks
            
            for i in range(0, len(sentences), chunk_size):
                chunk = sentences[i:i+chunk_size]
                combined = " ".join(chunk)
                
                if combined.strip():
                    # Extract a simple title from first few words
                    words = combined.split()[:5]
                    title = " ".join(words).title()
                    
                    lines.append(f"\n### {title}...")
                    lines.append(f"• {combined[:200]}...")
                    lines.append("")
        
        return "\n".join(lines)

    def combine_segments(self, segments: List[Dict]) -> str:
        """
        Combine transcript segments into continuous text
        """
        return " ".join([seg.get("text", "") for seg in segments])
