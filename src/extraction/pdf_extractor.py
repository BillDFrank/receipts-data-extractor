import pdfplumber
from typing import Optional
import io


class PDFExtractor:
    """Utility class for extracting text from PDF files."""

    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> Optional[str]:
        """
        Extract text content from PDF bytes.

        Args:
            pdf_content: Raw PDF file content as bytes

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    @staticmethod
    def extract_text_from_file(file_path: str) -> Optional[str]:
        """
        Extract text content from PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF file {file_path}: {e}")
            return None
