import json
import os
import tempfile
from pathlib import Path

import pytest

# Try importing PDF libraries to decide whether to skip tests
try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

if not HAS_PYPDF2 and not HAS_PDFPLUMBER:
    pytest.skip("No PDF library available", allow_module_level=True)

from servers.pdf_skill.server import (
    convert_pdf_to_text_file,
    extract_pages_from_pdf,
    extract_text_from_pdf,
    get_pdf_info,
)


def create_sample_pdf(path: str):
    """Create a simple PDF for testing using reportlab if available, else skip."""
    try:
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(path)
        c.drawString(100, 750, "Sample PDF Page 1")
        c.showPage()
        c.drawString(100, 750, "Sample PDF Page 2")
        c.showPage()
        c.save()
    except ImportError:
        # If reportlab not installed, create a dummy PDF file (invalid) and skip tests
        with open(path, "wb") as f:
            f.write(b"%PDF dummy")
        pytest.skip(
            "reportlab not installed, cannot create valid PDF", allow_module_level=True
        )


def test_extract_text_from_pdf():
    """Test extracting text from PDF."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "sample.pdf"
        create_sample_pdf(str(pdf_path))
        result = extract_text_from_pdf(str(pdf_path))
        # Should contain at least "Sample"
        assert "Sample" in result


def test_extract_pages_from_pdf():
    """Test extracting specific pages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "sample.pdf"
        create_sample_pdf(str(pdf_path))
        result = extract_pages_from_pdf(str(pdf_path), json.dumps([1]))
        assert "Page 1" in result or "Sample" in result


def test_get_pdf_info():
    """Test retrieving PDF info."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "sample.pdf"
        create_sample_pdf(str(pdf_path))
        result = get_pdf_info(str(pdf_path))
        info = json.loads(result)
        assert info["num_pages"] == 2


def test_convert_pdf_to_text_file():
    """Test converting PDF to text file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "sample.pdf"
        txt_path = Path(tmpdir) / "output.txt"
        create_sample_pdf(str(pdf_path))
        result = convert_pdf_to_text_file(str(pdf_path), str(txt_path))
        assert "Successfully" in result
        assert txt_path.exists()
        text = txt_path.read_text()
        assert "Sample" in text
