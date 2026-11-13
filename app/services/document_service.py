"""
SkillBridge AI - Document Text Extraction Service
Safely extracts and normalizes text from PDF, DOCX, and TXT resume files.
"""

import os
from pathlib import Path
import re
from typing import Tuple

def extract_text_from_file(file_path: Path) -> Tuple[bool, str, str]:
    """
    Extracts text from a given file path (.pdf, .docx, .txt).
    Returns (success: bool, text: str, message: str)
    """
    if not file_path.exists():
        return False, "", f"File does not exist: {file_path}"

    ext = file_path.suffix.lower()

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return True, clean_extracted_text(text), "Text file processed successfully."

        elif ext == ".docx":
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            full_text = "\n".join(paragraphs)
            return True, clean_extracted_text(full_text), "DOCX file processed successfully."

        elif ext == ".pdf":
            # First try PyMuPDF (fitz) or pypdf/pdfplumber
            extracted = []
            try:
                import fitz # PyMuPDF
                doc = fitz.open(file_path)
                for page in doc:
                    extracted.append(page.get_text())
                doc.close()
            except ImportError:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        extracted.append(txt)

            full_text = "\n".join(extracted).strip()
            if not full_text or len(full_text) < 50:
                return False, "", "PDF contains little or no text. It might be a scanned image document requiring OCR."

            return True, clean_extracted_text(full_text), "PDF file processed successfully."

        else:
            return False, "", f"Unsupported file extension: {ext}. Allowed formats: PDF, DOCX, TXT."

    except Exception as e:
        return False, "", f"Error reading document: {str(e)}"

def clean_extracted_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    if not text:
        return ""
    # Remove control chars
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    # Normalize multiple newlines and spaces
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()
