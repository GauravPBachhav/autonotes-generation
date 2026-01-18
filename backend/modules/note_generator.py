"""
Note Generator Module
Formats and exports notes to multiple formats (Markdown, PDF, Docx)
"""

import os
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
import markdown

logger = logging.getLogger(__name__)


class NoteGenerator:
    """Generate formatted notes in multiple formats"""

    def __init__(self, output_dir: str = "./output"):
        """
        Initialize Note Generator
        
        Args:
            output_dir: Directory to save generated notes
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_note_content(
        self,
        title: str,
        transcript_data: Dict,
        processed_data: Dict,
        summaries: Dict,
    ) -> Dict[str, str]:
        """
        Generate structured note content in multiple formats
        
        Args:
            title: Lecture title
            transcript_data: Transcription results
            processed_data: Processed text data
            summaries: Summary data
            
        Returns:
            Dictionary with markdown, html, and text formats
        """
        logger.info(f"Generating note content for: {title}")

        # Build markdown content
        markdown_content = self._build_markdown(
            title,
            transcript_data,
            processed_data,
            summaries,
        )

        # Convert to HTML
        html_content = markdown.markdown(markdown_content)

        # Plain text version
        text_content = self._extract_plain_text(markdown_content)

        content = {
            "markdown": markdown_content,
            "html": html_content,
            "text": text_content,
        }

        logger.info("Note content generated successfully")
        return content

    def _build_markdown(
        self,
        title: str,
        transcript_data: Dict,
        processed_data: Dict,
        summaries: Dict,
    ) -> str:
        """Build markdown formatted note"""
        md = []

        # Header
        md.append(f"# {title}\n")
        md.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        md.append(f"**Duration:** {transcript_data.get('duration', 'N/A')} seconds\n")
        md.append(f"**Language:** {transcript_data.get('language', 'N/A')}\n\n")

        # Table of Contents
        md.append("## Table of Contents\n")
        md.append("- [📝 Simplified Notes](#simplified-notes)\n")
        md.append("- [🎙️ Full Transcription](#full-transcription)\n\n")

        # PART 1: SIMPLIFIED NOTES
        md.append("---\n\n")
        md.append("# 📝 Simplified Notes\n")
        md.append("*Easy-to-read, organized version with key points*\n\n")

        # Executive Summary
        md.append("## Summary\n\n")
        md.append(f"{summaries.get('overall_summary', 'Well-organized lecture notes')}\n\n")

        # Key Points
        md.append("## Key Points\n\n")
        for i, point in enumerate(summaries.get('bullet_points', []), 1):
            md.append(f"{i}. {point}\n")
        md.append("\n")

        # Keywords
        md.append("## Key Terms & Concepts\n\n")
        for keyword in processed_data.get('keywords', [])[:10]:
            md.append(f"- {keyword}\n")
        md.append("\n")

        # Simplified Sections
        md.append("## Main Topics\n\n")
        for i, section in enumerate(processed_data.get('sections', [])[:5], 1):  # Show top 5 sections
            section_text = section.get('text', '')
            
            if len(section_text) > 300:
                section_text = section_text[:300] + "..."
            
            md.append(f"### Topic {i}\n\n")
            md.append(f"{section_text}\n\n")

        # PART 2: FULL TRANSCRIPTION
        md.append("---\n\n")
        md.append("# 🎙️ Full Transcription\n")
        md.append("*Complete word-by-word transcript from audio*\n\n")
        md.append(f"{processed_data.get('cleaned_text', 'N/A')}\n\n")
        
        # Statistics
        md.append("---\n\n")
        md.append("## Statistics\n\n")
        md.append(f"- **Word Count:** {processed_data.get('word_count', 0)}\n")
        md.append(f"- **Sentence Count:** {processed_data.get('sentence_count', 0)}\n")
        md.append(f"- **Duration:** {transcript_data.get('duration', 'N/A')} seconds\n")
        md.append(f"- **Language:** {transcript_data.get('language', 'N/A')}\n")

        return "".join(md)

    def export_markdown(self, content: str, filename: str) -> str:
        """Export note to Markdown file"""
        try:
            output_path = os.path.join(self.output_dir, f"{filename}.md")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"Markdown file saved: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to export Markdown: {e}")
            raise

    def export_pdf(self, markdown_content: str, filename: str, title: str = "Notes") -> str:
        """Export note to PDF file"""
        try:
            output_path = os.path.join(self.output_dir, f"{filename}.pdf")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, title, ln=True, align="C")
            
            pdf.set_font("Arial", "", 11)
            pdf.ln(5)

            # Convert markdown to text for PDF
            text = self._extract_plain_text(markdown_content)
            
            # Add text with word wrapping
            for line in text.split("\n"):
                if line.strip():
                    pdf.multi_cell(0, 5, line)
                else:
                    pdf.ln(3)

            pdf.output(output_path)
            
            logger.info(f"PDF file saved: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            raise

    def export_docx(self, markdown_content: str, filename: str, title: str = "Notes") -> str:
        """Export note to DOCX file"""
        try:
            output_path = os.path.join(self.output_dir, f"{filename}.docx")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            doc = Document()

            # Title
            title_para = doc.add_heading(title, level=1)
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Add timestamp
            timestamp = doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            timestamp.style = "Normal"

            # Add content from markdown
            doc.add_paragraph(markdown_content)

            doc.save(output_path)
            
            logger.info(f"DOCX file saved: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to export DOCX: {e}")
            raise

    def _extract_plain_text(self, markdown_content: str) -> str:
        """Extract plain text from markdown"""
        # Remove markdown syntax
        text = markdown_content
        text = text.replace("# ", "").replace("## ", "").replace("### ", "")
        text = text.replace("**", "").replace("*", "").replace("_", "")
        text = text.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        return text

    def export_all_formats(
        self,
        note_content: Dict,
        filename: str,
        title: str = "Lecture Notes",
    ) -> Dict[str, str]:
        """
        Export note to all available formats
        
        Returns:
            Dictionary with paths to all exported files
        """
        logger.info(f"Exporting all formats for: {filename}")
        
        markdown_path = self.export_markdown(note_content["markdown"], filename)
        pdf_path = self.export_pdf(note_content["markdown"], filename, title)
        docx_path = self.export_docx(note_content["markdown"], filename, title)

        result = {
            "markdown": markdown_path,
            "pdf": pdf_path,
            "docx": docx_path,
        }

        logger.info(f"All formats exported successfully")
        return result
