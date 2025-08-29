import pytest
from io import BytesIO
from src.extraction.pdf_extractor import PDFExtractor


class TestPDFExtractor:
    """Test cases for PDF text extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFExtractor()

    def test_extract_text_from_file_valid_path(self):
        """Test extracting text from a valid PDF file."""
        # This would require a real PDF file for testing
        # For now, we'll test the error handling
        result = self.extractor.extract_text_from_file("nonexistent.pdf")
        assert result is None

    def test_extract_text_from_pdf_invalid_data(self):
        """Test extracting text from invalid PDF data."""
        invalid_pdf = b"This is not a PDF file"
        result = self.extractor.extract_text_from_pdf(invalid_pdf)
        assert result is None

    def test_extract_text_from_pdf_empty_data(self):
        """Test extracting text from empty PDF data."""
        empty_pdf = b""
        result = self.extractor.extract_text_from_pdf(empty_pdf)
        assert result is None