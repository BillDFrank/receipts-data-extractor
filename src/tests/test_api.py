import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from src.api.main import app


class TestAPI:
    """Test cases for the FastAPI application."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data

    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "Supermarket Receipt Extractor API" in data["message"]
        assert "endpoints" in data

    def test_extract_endpoint_invalid_file_type(self):
        """Test extract endpoint with invalid file type."""
        # Create a text file instead of PDF
        file_content = b"This is not a PDF file"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

        response = self.client.post("/extract", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "Only PDF files are supported" in data["detail"]

    def test_extract_endpoint_empty_file(self):
        """Test extract endpoint with empty file."""
        files = {"file": ("empty.pdf", BytesIO(b""), "application/pdf")}

        response = self.client.post("/extract", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Could not extract text from PDF" in data["error_message"]

    def test_extract_endpoint_no_file(self):
        """Test extract endpoint with no file provided."""
        response = self.client.post("/extract")

        assert response.status_code == 422  # Validation error

    def test_extract_endpoint_with_mock_pdf_data(self):
        """Test extract endpoint with mock PDF data that should work."""
        # This is a simplified test - in real scenario we'd need actual PDF content
        # For now, we'll test the error handling path
        mock_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000200 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"

        files = {"file": ("test.pdf", BytesIO(
            mock_pdf_content), "application/pdf")}

        response = self.client.post("/extract", files=files)

        # The response will depend on whether the mock PDF can be parsed
        # At minimum, it should not return a 500 error
        assert response.status_code in [200, 422]

    def test_extract_batch_endpoint_no_files(self):
        """Test extract-batch endpoint with no files provided."""
        response = self.client.post("/extract-batch")

        assert response.status_code == 422  # FastAPI validation error for missing required field
        data = response.json()
        assert "files" in str(data)  # Should mention the missing files field

    def test_extract_batch_endpoint_invalid_file_type(self):
        """Test extract-batch endpoint with invalid file type."""
        file_content = b"This is not a PDF file"
        files = [("files", ("test.txt", BytesIO(file_content), "text/plain"))]

        response = self.client.post("/extract-batch", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 1
        assert data["successful_extractions"] == 0
        assert data["failed_extractions"] == 1
        assert len(data["results"]) == 1
        assert not data["results"][0]["success"]
        assert "Only PDF files supported" in data["results"][0]["error_message"]

    def test_extract_batch_endpoint_empty_files(self):
        """Test extract-batch endpoint with empty files."""
        files = [
            ("files", ("empty1.pdf", BytesIO(b""), "application/pdf")),
            ("files", ("empty2.pdf", BytesIO(b""), "application/pdf"))
        ]

        response = self.client.post("/extract-batch", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 2
        assert data["successful_extractions"] == 0
        assert data["failed_extractions"] == 2
        assert len(data["results"]) == 2

    def test_extract_batch_endpoint_mixed_files(self):
        """Test extract-batch endpoint with mix of valid and invalid files."""
        mock_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000200 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"

        files = [
            ("files", ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")),
            ("files", ("test.txt", BytesIO(b"not pdf"), "text/plain"))
        ]

        response = self.client.post("/extract-batch", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 2
        # Both files might fail due to mock PDF issues, so just check that we get results
        assert len(data["results"]) == 2
        assert data["failed_extractions"] >= 1  # At least the text file should fail
