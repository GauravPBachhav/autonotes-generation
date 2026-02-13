"""
Text Processing Module
Cleans, segments, and extracts key information from transcripts.
Generates structured topic-wise notes from raw transcription.
Handles unpunctuated speech-recognition output.
"""

import re
import logging
from typing import List, Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# Expanded stop words
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from',
    'has', 'have', 'had', 'he', 'she', 'her', 'his', 'him', 'how', 'i',
    'if', 'in', 'is', 'it', 'its', 'just', 'let', 'may', 'me', 'my',
    'no', 'nor', 'not', 'now', 'of', 'on', 'or', 'our', 'out', 'own',
    'say', 'says', 'so', 'some', 'such', 'than', 'that', 'the', 'them',
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to',
    'too', 'under', 'up', 'us', 'very', 'was', 'we', 'were', 'what',
    'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will',
    'with', 'would', 'you', 'your', 'also', 'been', 'can', 'could',
    'did', 'do', 'does', 'each', 'get', 'got', 'here', 'into',
    'more', 'much', 'must', 'need', 'only', 'other', 'shall',
    'should', 'about', 'above', 'after', 'again', 'all', 'am', 'any',
    'because', 'before', 'being', 'below', 'between', 'both', 'come',
    'going', 'gonna', 'okay', 'right', 'well', 'thing', 'things',
    'really', 'actually', 'know', 'think', 'see', 'look', 'make',
    'want', 'way', 'one', 'two', 'three', 'first', 'second', 'new',
    'like', 'time', 'even', 'back', 'still', 'take', 'give', 'use',
    'used', 'using', 'uses',
}

# Words that strongly signal start of a new sentence in spoken language
SENTENCE_STARTERS = {
    # Pronouns → strong signal of a new sentence as subject
    'it', 'this', 'that', 'these', 'those', 'there',
    'they', 'we', 'you', 'he', 'she',
    # Transitions
    'so', 'now', 'also', 'another', 'next',
    'first', 'second', 'third', 'finally', 'lastly',
    'however', 'therefore', 'moreover', 'furthermore',
    'basically', 'essentially', 'actually',
    'let', 'remember', 'note',
    # Subordinators that often start a new thought in speech
    'when', 'while', 'if', 'since', 'because',
}

# Trailing words that should NOT end a sentence (we re-attach them)
TRAILING_JUNK = {'the', 'a', 'an', 'of', 'to', 'in', 'for', 'with', 'and',
                 'or', 'but', 'than', 'is', 'are', 'was', 'its', 'by',
                 'on', 'at', 'from', 'as'}

QUESTION_WORDS = {'what', 'how', 'why', 'when', 'where', 'who', 'which'}


class TextProcessor:
    """Process and structure raw transcripts into organized notes"""

    def __init__(self):
        self.stop_words = STOP_WORDS

    # ------------------------------------------------------------------ #
    #  PUNCTUATION RESTORATION (core fix for speech-recognition text)
    # ------------------------------------------------------------------ #

    def _add_sentence_boundaries(self, text: str) -> str:
        """
        Insert periods/question-marks into unpunctuated speech-recognition text.
        Without this, the entire transcript is treated as ONE sentence and every
        section shows identical content.
        """
        period_count = len(re.findall(r'[.!?]', text))
        words = text.split()
        word_count = len(words)

        if word_count == 0:
            return text

        # Already has reasonable punctuation → skip
        if period_count >= max(1, word_count / 25):
            return text

        logger.info("Transcript lacks punctuation – adding sentence boundaries")

        result: List[str] = []
        since_break = 0  # words since last sentence boundary

        for i, word in enumerate(words):
            lower = word.lower().strip('.,!?;:')

            insert_break = False
            is_question = False

            if i > 0:
                # Question word after 6+ words → likely new question sentence
                if lower in QUESTION_WORDS and since_break >= 6:
                    insert_break = True
                    is_question = True

                # Common sentence starters after 10+ words
                elif lower in SENTENCE_STARTERS and since_break >= 10:
                    insert_break = True

                # Force a break after ~22 words with no boundary
                elif since_break >= 22:
                    insert_break = True

            if insert_break and result:
                last = result[-1]
                if not last[-1:] in '.!?;:':
                    result[-1] = last + ('?' if is_question else '.')
                since_break = 0

            # Capitalize first word of new sentence
            if since_break == 0 and word[:1].isalpha():
                word = word[0].upper() + word[1:]

            result.append(word)
            since_break += 1

        # Ensure text ends with a period
        if result and result[-1][-1:] not in '.!?':
            result[-1] = result[-1] + '.'

        text = ' '.join(result)

        # Clean up: sentences should not end with trailing articles/prepositions
        text = self._fix_trailing_junk(text)

        return text

    @staticmethod
    def _fix_trailing_junk(text: str) -> str:
        """Move trailing articles/prepositions from end of sentence to start of next."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cleaned: List[str] = []
        carry = ''
        for s in sentences:
            if carry:
                s = carry + ' ' + s[0].lower() + s[1:] if s else carry
                carry = ''
            # Check if sentence ends with junk word before punctuation
            m = re.match(r'^(.*?)\s+(\w+)([.!?])$', s)
            if m:
                body, last_word, punct = m.group(1), m.group(2), m.group(3)
                if last_word.lower() in TRAILING_JUNK and len(body.split()) >= 3:
                    s = body + punct
                    carry = last_word.capitalize()
            cleaned.append(s)
        if carry:
            # Attach leftover to last sentence
            if cleaned:
                cleaned[-1] = cleaned[-1].rstrip('.!?') + ' ' + carry.lower() + '.'
        return ' '.join(cleaned)

    # ------------------------------------------------------------------ #
    #  CLEANING
    # ------------------------------------------------------------------ #

    def clean_text(self, text: str) -> str:
        """Clean transcript text and restore punctuation if missing."""
        text = re.sub(r'\s+', ' ', text).strip()

        filler_patterns = [
            r'\b(um|uh|ah|er|erm)\b',
            r'\[.*?\]',
            r'\(.*?\)',
        ]
        for pattern in filler_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        text = re.sub(r'\s+', ' ', text).strip()

        # Restore sentence boundaries for unpunctuated speech text
        text = self._add_sentence_boundaries(text)

        return text

    # ------------------------------------------------------------------ #
    #  SENTENCE / TOPIC SEGMENTATION
    # ------------------------------------------------------------------ #

    def segment_by_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = [s.strip() for s in sentences if s.strip()]
        # Fallback: split on period chars
        if len(result) <= 1 and len(text) > 80:
            result = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        return result

    def _detect_topic_boundaries(self, sentences: List[str]) -> List[int]:
        """Detect where topics change using content-similarity heuristics."""
        if len(sentences) <= 3:
            return [0]

        boundaries = [0]

        def _keywords(s: str):
            return {w for w in s.lower().split()
                    if w.isalpha() and w not in self.stop_words and len(w) > 2}

        prev_kw = _keywords(sentences[0])

        for i in range(1, len(sentences)):
            cur_kw = _keywords(sentences[i])
            # Topic shift → low keyword overlap with previous sentence
            overlap = len(prev_kw & cur_kw)
            union = len(prev_kw | cur_kw) or 1
            similarity = overlap / union

            if similarity < 0.25 and i - boundaries[-1] >= 2:
                boundaries.append(i)

            prev_kw = cur_kw

        return boundaries

    def _generate_topic_title(self, text: str, topic_keywords: List[str]) -> str:
        """Generate a concise topic title."""
        patterns = [
            r'(?:what\s+is|definition\s+of|means?)\s+(.{5,50}?)(?:[.!?,]|$)',
            r'(?:about|discuss|cover|explore|understand)\s+(.{5,50}?)(?:[.!?,]|$)',
            r'(?:introduction\s+to|intro\s+to)\s+(.{5,50}?)(?:[.!?,]|$)',
        ]
        lower = text.lower()
        for pat in patterns:
            m = re.search(pat, lower)
            if m:
                words = m.group(1).strip().split()
                if len(words) > 6:
                    words = words[:6]
                return ' '.join(words).title()

        if topic_keywords:
            return ' '.join(topic_keywords[:4]).title()

        words = [w for w in text.split()[:8] if w.lower() not in self.stop_words]
        return ' '.join(words[:4]).title() if words else "Topic"

    def segment_by_topics(self, text: str) -> List[Dict]:
        """Segment text into topic-based sections."""
        sentences = self.segment_by_sentences(text)
        if not sentences:
            return []

        boundaries = self._detect_topic_boundaries(sentences)

        # Fall back to even chunks when no boundaries detected
        if len(boundaries) <= 1 and len(sentences) > 4:
            chunk = max(3, len(sentences) // max(2, len(sentences) // 4))
            boundaries = list(range(0, len(sentences), chunk))

        topics = []
        for idx, start in enumerate(boundaries):
            end = boundaries[idx + 1] if idx + 1 < len(boundaries) else len(sentences)
            sec_sents = sentences[start:end]
            sec_text = ' '.join(sec_sents)
            sec_kw = self.extract_keywords(sec_text, top_n=5)
            title = self._generate_topic_title(sec_text, sec_kw)

            topics.append({
                "title": title,
                "text": sec_text,
                "sentences": sec_sents,
                "keywords": sec_kw,
                "sentence_count": len(sec_sents),
                "word_count": len(sec_text.split()),
            })

        return topics

    def segment_by_sections(self, text: str, max_section_length: int = 500) -> List[Dict]:
        return self.segment_by_topics(text)

    # ------------------------------------------------------------------ #
    #  KEYWORD / PHRASE EXTRACTION
    # ------------------------------------------------------------------ #

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        words = text.lower().split()
        bigrams = []
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            if (w1.isalpha() and w2.isalpha()
                    and w1 not in self.stop_words
                    and w2 not in self.stop_words
                    and len(w1) > 2 and len(w2) > 2):
                bigrams.append(f"{w1} {w2}")
        return [p for p, _ in Counter(bigrams).most_common(top_n)]

    def extract_keywords(self, text: str, top_n: int = 15) -> List[str]:
        words = text.lower().split()
        kws = [w for w in words if w.isalnum() and w not in self.stop_words and len(w) > 2]
        return [w for w, _ in Counter(kws).most_common(top_n)]

    # ------------------------------------------------------------------ #
    #  CONDENSATION HELPERS (turn raw sentences into SHORT note points)
    # ------------------------------------------------------------------ #

    def _condense_to_point(self, sentence: str, max_words: int = 14) -> str:
        """Turn a full spoken sentence into a short note-style bullet point."""
        s = sentence.strip().rstrip('.!?')

        # Strip filler openings
        for pat in [
            r'^(so|well|now|okay|basically|essentially|actually|right)\s+',
            r'^(it is|it can be|there is|there are|we have|we can|you can)\s+',
            r'^(this is|that is|these are|those are)\s+',
            r'^(as we know|as mentioned|as i said)\s+',
        ]:
            s = re.sub(pat, '', s, flags=re.IGNORECASE).strip()

        if s:
            s = s[0].upper() + s[1:]

        # Truncate to max_words
        words = s.split()
        if len(words) > max_words:
            # Try to cut at a natural boundary (before a preposition/conjunction)
            cut = max_words
            for j in range(max_words, max(max_words - 3, 4), -1):
                if words[j].lower() in {'the', 'a', 'an', 'of', 'to', 'in', 'for',
                                          'with', 'and', 'or', 'but', 'than', 'by', 'on'}:
                    cut = j
                    break
            s = ' '.join(words[:cut])

        # Remove trailing junk words
        while s:
            last = s.split()[-1].lower() if s.split() else ''
            if last in {'the', 'a', 'an', 'of', 'to', 'in', 'for', 'and', 'or', 'than', 'is', 'are', 'by'}:
                s = ' '.join(s.split()[:-1])
            else:
                break

        return s

    def _make_takeaway(self, sentence: str) -> str:
        """Turn a sentence into a labelled takeaway like 'Purpose: ...'."""
        low = sentence.lower()

        label_patterns = [
            (r'(?:is|are)\s+used\s+for\s+(.+)', 'Purpose'),
            (r'used\s+(?:for|to)\s+(.+)', 'Purpose'),
            (r'(?:can|could)\s+be\s+applied\s+to\s+(.+)', 'Applies to'),
            (r'applied\s+to\s+(.+)', 'Applies to'),
            (r'belongs?\s+to\s+(.+)', 'Scope'),
            (r'(?:is|are)\s+(?:a|an|the)\s+(.+)', 'Definition'),
            (r'refers?\s+to\s+(.+)', 'Means'),
            (r'means?\s+(.+)', 'Means'),
            (r'(?:advantage|benefit)\s+(?:of|is)\s+(.+)', 'Advantage'),
            (r'(?:disadvantage|drawback)\s+(?:of|is)\s+(.+)', 'Disadvantage'),
            (r'types?\s+(?:of|include|are)\s+(.+)', 'Types'),
            (r'example\s+(?:of|is|:)\s*(.+)', 'Example'),
        ]

        for pat, label in label_patterns:
            m = re.search(pat, low)
            if m:
                rest = m.group(1).strip().rstrip('.!?')
                rest = rest[0].upper() + rest[1:] if rest else rest
                words = rest.split()
                if len(words) > 7:
                    # Cut before trailing junk
                    cut = 7
                    for j in range(7, max(4, 7 - 2), -1):
                        if words[j].lower() in TRAILING_JUNK:
                            cut = j
                            break
                    rest = ' '.join(words[:cut])
                return f"{label}: {rest}"

        # Fallback: condense differently from bullet (shorter, with →)
        condensed = self._condense_to_point(sentence, max_words=10)
        return condensed

    # ------------------------------------------------------------------ #
    #  DEFINITION EXTRACTION
    # ------------------------------------------------------------------ #

    def _extract_definitions(self, text: str) -> List[Dict[str, str]]:
        """Extract term-definition pairs from the text."""
        definitions = []
        patterns = [
            r'([A-Z][a-zA-Z\s]{2,30}?)\s+(?:is|are|means?|refers?\s+to|can\s+be\s+defined\s+as)\s+(.{15,200}?)(?:\.|!|\?|$)',
            r'(?:definition\s+of|define)\s+([a-zA-Z\s]{2,30}?)\s*[:\-]?\s*(.{15,200}?)(?:\.|$)',
        ]

        # Reject terms that are articles, question words, pronouns, or junk
        reject_terms = {
            'the', 'a', 'an',
            'what', 'how', 'why', 'when', 'where', 'who', 'which',
            'it', 'this', 'that', 'these', 'those', 'there', 'they',
            'we', 'you', 'he', 'she', 'because', 'since', 'also',
            'ted', 'ing', 'ed', 'tion', 'ment',  # fragments
        }

        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                term = m.group(1).strip()
                defn = m.group(2).strip().rstrip('.!?')
                term_lower = term.lower().strip()

                # Filter out noisy matches
                if term_lower in reject_terms:
                    continue
                term_words = term.split()
                if len(term_words) < 1 or len(term_words) > 4:
                    continue
                if len(defn.split()) < 3:
                    continue
                # No word in the term should be a reject word
                if any(tw.lower() in reject_terms for tw in term_words):
                    continue
                # Term should have at least one content word > 3 chars
                if not any(len(tw) > 3 and tw.lower() not in STOP_WORDS for tw in term_words):
                    continue

                definitions.append({"term": term.title(), "definition": defn})

        seen = set()
        unique = []
        for d in definitions:
            if d["term"] not in seen:
                seen.add(d["term"])
                unique.append(d)
        return unique[:10]

    # ------------------------------------------------------------------ #
    #  STRUCTURED NOTES GENERATION  (each section genuinely different)
    # ------------------------------------------------------------------ #

    def _generate_structured_notes(self, text: str, topics: List[Dict], keywords: List[str]) -> Dict:
        """
        Generate well-structured notes where every section is genuinely different:
          - topics[]   → SHORT condensed bullet points per topic
          - key_takeaways[] → labelled takeaways (Purpose: / Scope: / etc.)
          - definitions[]   → term-definition pairs
          - quick_revision[] → ultra-short one-liners
        """
        notes: Dict = {
            "topics": [],
            "definitions": [],
            "key_takeaways": [],
            "quick_revision": [],
        }

        # ── Topic notes: condensed bullets (not raw sentences) ──
        for topic in topics:
            topic_note = {
                "title": topic["title"],
                "content": topic["text"],
                "keywords": topic["keywords"],
                "bullet_points": [],
            }
            for sent in topic.get("sentences", []):
                if len(sent.split()) >= 4:
                    point = self._condense_to_point(sent, max_words=12)
                    if point and len(point.split()) >= 3:
                        topic_note["bullet_points"].append(point)
            notes["topics"].append(topic_note)

        # ── Definitions ──
        notes["definitions"] = self._extract_definitions(text)

        # ── Key takeaways: labelled / categorised points ──
        all_sentences = self.segment_by_sentences(text)
        scored: List[Tuple[str, float]] = []
        for s in all_sentences:
            low = s.lower()
            score = 0.0
            for kw in keywords[:10]:
                if kw in low:
                    score += 2
            wc = len(s.split())
            if 8 <= wc <= 35:
                score += 2
            if re.search(r'\b(is|are|means|used|applied|belongs?|refers?|called|defined)\b', low):
                score += 3
            scored.append((s, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        seen_ta: set = set()
        for s, sc in scored:
            if sc <= 0:
                break
            ta = self._make_takeaway(s)
            if not ta or len(ta.split()) < 3:
                continue
            ta_key = ta.lower()[:30]
            if ta_key not in seen_ta:
                seen_ta.add(ta_key)
                notes["key_takeaways"].append(ta)
            if len(notes["key_takeaways"]) >= 6:
                break

        # ── Quick revision: ultra-short one-liner per topic ──
        for topic in topics:
            kws = topic.get("keywords", [])
            title = topic.get("title", "Topic")
            if kws:
                notes["quick_revision"].append(f"{title} → {', '.join(kws[:3])}")
            else:
                # Super-condense the first sentence of this topic
                first = (topic.get("sentences") or [""])[0]
                short = self._condense_to_point(first, max_words=8)
                if short:
                    notes["quick_revision"].append(f"{title} → {short}")

        return notes

    # ------------------------------------------------------------------ #
    #  MAIN PIPELINE
    # ------------------------------------------------------------------ #

    def process_transcript(self, text: str) -> Dict:
        """Full processing pipeline."""
        logger.info("Starting text processing")

        cleaned_text = self.clean_text(text)      # includes punctuation fix
        topics = self.segment_by_topics(cleaned_text)
        key_phrases = self.extract_key_phrases(cleaned_text)
        keywords = self.extract_keywords(cleaned_text)
        structured_notes = self._generate_structured_notes(cleaned_text, topics, keywords)

        processed = {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "structured_notes": structured_notes,
            "sections": topics,
            "section_count": len(topics),
            "key_phrases": key_phrases,
            "keywords": keywords,
            "word_count": len(cleaned_text.split()),
            "sentence_count": len(self.segment_by_sentences(cleaned_text)),
        }

        logger.info(f"Processing complete. Topics: {len(topics)}, Words: {processed['word_count']}")
        return processed

    def combine_segments(self, segments: List[Dict]) -> str:
        return " ".join([seg.get("text", "") for seg in segments])
