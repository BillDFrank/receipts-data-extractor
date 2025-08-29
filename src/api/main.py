from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from ..extraction.pdf_extractor import PDFExtractor
from ..extraction.receipt_parser import PingoDoceReceiptParser
from ..extraction.models import ExtractionResult, HealthResponse

app = FastAPI(
    title="Supermarket Receipt Extractor API",
    description="API for extracting product information from supermarket receipts",
    version="1.0.0"
)

pdf_extractor = PDFExtractor()
receipt_parser = PingoDoceReceiptParser()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Supermarket Receipt Extractor API is running"
    )


@app.post("/extract", response_model=ExtractionResult)
async def extract_receipt(file: UploadFile = File(...)):
    """
    Extract product information from uploaded PDF receipt.

    Args:
        file: PDF file containing the supermarket receipt

    Returns:
        ExtractionResult with parsed receipt data or error message
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        # Read file content
        pdf_content = await file.read()

        # Extract text from PDF
        text = pdf_extractor.extract_text_from_pdf(pdf_content)
        if not text:
            return ExtractionResult(
                success=False,
                error_message="Could not extract text from PDF"
            )

        # Parse receipt
        result = receipt_parser.parse_receipt(text)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing receipt: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Supermarket Receipt Extractor API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "POST /extract": "Extract receipt data from PDF"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)