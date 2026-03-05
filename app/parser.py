"""
parser.py — Extract and clean text from uploaded PDF or DOCX resumes.
"""

import re
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO


# ── Section keywords to detect ───────────────────────────────────────────────
SECTION_PATTERNS = {
    "skills":     r"\b(skills?|technical skills?|core competencies|technologies)\b",
    "experience": r"\b(experience|work experience|employment|career history|professional background)\b",
    "education":  r"\b(education|academic|degree|university|college|school)\b",
    "projects":   r"\b(projects?|personal projects?|portfolio|open.?source)\b",
    "summary":    r"\b(summary|profile|objective|about me|introduction)\b",
    "certifications": r"\b(certifications?|certificates?|licenses?|credentials?)\b",
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF file using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract raw text from a .docx file."""
    doc = Document(BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def clean_text(raw: str) -> str:
    """Normalize whitespace, remove junk characters, collapse blank lines."""
    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]", " ", raw)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Collapse 3+ consecutive newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_sections(text: str) -> dict[str, str]:
    """
    Split resume text into named sections based on keyword detection.
    Returns a dict like { "experience": "...", "skills": "..." }.
    Lines that don't fall under a detected heading go into "general".
    """
    lines = text.split("\n")
    sections: dict[str, list[str]] = {"general": []}
    current = "general"

    for line in lines:
        stripped = line.strip()
        matched = False
        for section, pattern in SECTION_PATTERNS.items():
            # Treat as a heading if short line matches a section keyword
            if len(stripped) < 60 and re.search(pattern, stripped, re.IGNORECASE):
                current = section
                if section not in sections:
                    sections[section] = []
                matched = True
                break
        if not matched:
            sections.setdefault(current, []).append(line)

    # Join lines per section, drop empty ones
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """
    Main entry point.
    Returns:
      {
        "full_text": str,
        "sections": { "experience": str, "skills": str, ... },
        "filename": str,
        "char_count": int,
      }
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        raw = extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".docx"):
        raw = extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Upload a PDF or DOCX.")

    cleaned = clean_text(raw)
    sections = detect_sections(cleaned)

    return {
        "filename": filename,
        "full_text": cleaned,
        "sections": sections,
        "char_count": len(cleaned),
    }
