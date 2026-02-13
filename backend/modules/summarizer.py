"""
Summarization Module
Generates COMPRESSED summaries and DISTINCT bullet points.
Each output section differs from processor's notes in format and selection.
"""

import re
import logging
from typing import List, Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

IMPORTANCE_MARKERS = [
    'important', 'key', 'significant', 'essential', 'crucial', 'main',
    'fundamental', 'primary', 'critical', 'core', 'basic', 'definition',
    'defined', 'means', 'refers', 'called', 'known', 'example', 'such as',
    'for instance', 'therefore', 'thus', 'hence', 'conclusion', 'result',
    'because', 'reason', 'purpose', 'advantage', 'disadvantage', 'benefit',
    'feature', 'property', 'characteristic', 'method', 'technique', 'process',
    'step', 'rule', 'principle', 'concept', 'type', 'types', 'category',
]


class Summarizer:
    """Generate compressed summaries and distinct bullet points."""

    def __init__(self, model_name: str = "simple", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        logger.info("Summarizer initialized (extractive mode)")

    # ------------------------------------------------------------------ #
    #  SCORING
    # ------------------------------------------------------------------ #

    def _score_sentence(self, sentence: str, word_freq: Dict[str, int], position: float) -> float:
        score = 0.0
        words = sentence.lower().split()
        wc = len(words)
        if wc < 4:
            return 0.0
        if wc > 50:
            score -= 1.0

        for w in words:
            if w in word_freq:
                score += word_freq[w] * 0.5

        lower = sentence.lower()
        for marker in IMPORTANCE_MARKERS:
            if marker in lower:
                score += 2.0

        if 8 <= wc <= 30:
            score += 2.0
        elif 5 <= wc <= 40:
            score += 1.0

        if position < 0.2:
            score += 1.5
        elif position > 0.9:
            score += 1.0

        if re.search(r'\d+', sentence):
            score += 0.5

        return score

    # ------------------------------------------------------------------ #
    #  COMPRESSION HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _compress_sentence(sentence: str) -> str:
        """Shorten a sentence by stripping filler and redundant words."""
        s = sentence.strip().rstrip('.!?')
        # Remove filler openings
        for pat in [
            r'^(so|well|now|okay|basically|essentially|actually|right)\s+',
            r'^(it is|it\'s|there is|there are)\s+(important|clear|evident|obvious)\s+(that|to)\s+',
            r'^(as we know|as we discussed|as mentioned|as i said|as i mentioned)\s*,?\s*',
            r'^(you know|you see|i think|i believe)\s*,?\s*',
        ]:
            s = re.sub(pat, '', s, flags=re.IGNORECASE).strip()
        # Capitalize
        if s:
            s = s[0].upper() + s[1:]
        return s

    def _merge_summary_sentences(self, sentences: List[str]) -> str:
        """Merge selected sentences into a flowing paragraph, removing redundancy."""
        if not sentences:
            return ""
        # Remove near-duplicates (keep the longer one)
        unique: List[str] = []
        seen_starts: set = set()
        for s in sentences:
            key = ' '.join(s.lower().split()[:5])
            if key not in seen_starts:
                seen_starts.add(key)
                unique.append(s)

        # Compress each sentence and join
        parts = [self._compress_sentence(s) for s in unique]
        parts = [p for p in parts if p]
        summary = '. '.join(parts)
        if summary and not summary.endswith('.'):
            summary += '.'
        return summary

    # ------------------------------------------------------------------ #
    #  SUMMARIZE (produces a SHORT paragraph — different from raw text)
    # ------------------------------------------------------------------ #

    def summarize(self, text: str, min_length: int = 100, max_length: int = 500) -> str:
        """
        Generate a genuinely COMPRESSED summary.
        Even for short texts, it compresses by removing filler and redundancy.
        """
        try:
            words = text.split()
            wc = len(words)

            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            # For very short text, just compress
            if wc < 30 or len(sentences) <= 1:
                compressed = self._compress_sentence(text)
                return compressed if compressed else text

            logger.info(f"Summarizing text ({wc} words, {len(sentences)} sentences)")

            # Build word frequency
            stop = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
                    'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                    'by', 'it', 'its', 'this', 'that', 'as', 'from', 'has', 'have',
                    'had', 'not', 'will', 'would', 'can', 'could', 'we', 'they', 'you',
                    'he', 'she', 'i', 'my', 'your', 'our', 'their', 'so', 'if'}
            word_list = [w.lower() for w in words if w.isalpha() and w.lower() not in stop and len(w) > 2]
            word_freq = Counter(word_list)

            # Score each sentence
            scored: List[Tuple[str, float, int]] = []
            for i, s in enumerate(sentences):
                pos = i / max(len(sentences), 1)
                sc = self._score_sentence(s, word_freq, pos)
                scored.append((s, sc, i))

            scored.sort(key=lambda x: x[1], reverse=True)

            # Pick top 40% of sentences (minimum 2, maximum 5)
            pick_count = max(2, min(5, len(sentences) * 2 // 5))
            selected = sorted(scored[:pick_count], key=lambda x: x[2])  # re-order by position
            chosen = [s for s, _, _ in selected]

            summary = self._merge_summary_sentences(chosen)

            if not summary:
                summary = self._merge_summary_sentences(sentences[:3])

            # Final check: if summary is still >= 90% of original, trim harder
            if len(summary.split()) > wc * 0.8 and len(sentences) > 2:
                # Just take top 2 scored sentences
                top2 = sorted(scored[:2], key=lambda x: x[2])
                summary = self._merge_summary_sentences([s for s, _, _ in top2])

            logger.info(f"Summary: {wc} words → {len(summary.split())} words")
            return summary

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return text

    # ------------------------------------------------------------------ #
    #  BULLET POINTS (distinct from processor's takeaways)
    # ------------------------------------------------------------------ #

    def extract_bullet_points(self, text: str, num_points: int = 8) -> List[str]:
        """
        Extract IMPORTANT POINTS as medium-length facts.
        These differ from processor's key_takeaways (which are labelled/categorised)
        and topic bullet_points (which are condensed per-topic).
        """
        try:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            if not sentences:
                return []

            words = [w.lower() for w in text.split() if w.isalpha() and len(w) > 3]
            word_freq = Counter(words)

            scored: List[Tuple[str, float]] = []
            for i, s in enumerate(sentences):
                wc = len(s.split())
                if wc < 4:
                    continue
                pos = i / max(len(sentences), 1)
                sc = self._score_sentence(s, word_freq, pos)
                scored.append((s, sc))

            scored.sort(key=lambda x: x[1], reverse=True)

            points: List[str] = []
            seen: set = set()
            for s, sc in scored:
                # Compress each sentence to medium length
                compressed = self._compress_sentence(s)
                if not compressed or len(compressed.split()) < 4:
                    continue

                # Truncate to medium length (max 18 words)
                cwords = compressed.split()
                if len(cwords) > 18:
                    compressed = ' '.join(cwords[:18])

                key = ' '.join(compressed.lower().split()[:5])
                if key in seen:
                    continue
                seen.add(key)

                # Ensure ends with period
                if not compressed.endswith(('.', '!', '?')):
                    compressed += '.'
                points.append(compressed)

                if len(points) >= num_points:
                    break

            logger.info(f"Extracted {len(points)} bullet points")
            return points

        except Exception as e:
            logger.warning(f"Bullet extraction failed: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  SECTION SUMMARIES
    # ------------------------------------------------------------------ #

    def summarize_sections(self, sections: List[Dict[str, str]], min_length: int = 50, max_length: int = 150) -> List[Dict]:
        summarized = []
        for i, section in enumerate(sections):
            try:
                text = section.get("text", "")
                summary = text if len(text.split()) < 20 else self.summarize(text, min_length, max_length)
                s = section.copy()
                s["summary"] = summary
                summarized.append(s)
            except Exception as e:
                logger.warning(f"Section {i+1} summarization failed: {e}")
                section["summary"] = section.get("text", "")
                summarized.append(section)
        return summarized
