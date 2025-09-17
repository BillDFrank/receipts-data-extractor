from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from typing import List
from ..extraction.pdf_extractor import PDFExtractor
from ..extraction.receipt_parser import SupermarketReceiptParser
from ..extraction.models import ExtractionResult, BatchExtractionResult, HealthResponse

app = FastAPI(
    title="Supermarket Receipt Extractor API",
    description="API for extracting product information from supermarket receipts",
    version="1.1.0"
)

pdf_extractor = PDFExtractor()
receipt_parser = SupermarketReceiptParser()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Supermarket Receipt Extractor API is running"
    )


@app.post("/extract-batch", response_model=BatchExtractionResult)
async def extract_receipts_batch(files: List[UploadFile] = File(...)):
    """
    Extract product information from multiple uploaded PDF receipts.

    Args:
        files: List of PDF files containing supermarket receipts

    Returns:
        BatchExtractionResult with list of parsed receipts and summary
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )

    results = []
    successful = 0
    failed = 0

    for file in files:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            results.append(ExtractionResult(
                success=False,
                error_message=f"{file.filename}: Only PDF files supported"
            ))
            failed += 1
            continue

        try:
            # Read file content
            pdf_content = await file.read()

            # Extract text from PDF
            text = pdf_extractor.extract_text_from_pdf(pdf_content)
            if not text:
                results.append(ExtractionResult(
                    success=False,
                    error_message=f"{file.filename}: Could not extract text"
                ))
                failed += 1
                continue

            # Parse receipt
            result = receipt_parser.parse_receipt(text)
            if result.success:
                successful += 1
            else:
                failed += 1
            results.append(result)

        except Exception as e:
            results.append(ExtractionResult(
                success=False,
                error_message=f"{file.filename}: Error processing: {str(e)}"
            ))
            failed += 1

    return BatchExtractionResult(
        results=results,
        total_files=len(files),
        successful_extractions=successful,
        failed_extractions=failed
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
        "version": "1.0.4",
        "endpoints": {
            "GET /health": "Health check",
            "POST /extract": "Extract receipt data from single PDF",
            "POST /extract-batch": "Extract receipt data from multiple PDFs"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
