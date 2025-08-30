# Supermarket Receipt Extractor API

A FastAPI-based service for extracting product information from supermarket receipts, specifically designed for Pingo Doce receipts.

## Features

- **PDF Text Extraction**: Extract text content from PDF receipt files
- **Product Parsing**: Parse product information including name, price, quantity, and discounts
- **FastAPI Integration**: RESTful API with automatic OpenAPI documentation
- **Pydantic Models**: Type-safe data models for extracted information
- **Comprehensive Testing**: Full test coverage for extraction logic and API endpoints

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd supermarket-transactions-extractor-from-pdf-1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
# or using uv
uv sync
```

## Usage

### Running the API

Start the FastAPI server:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "message": "Supermarket Receipt Extractor API is running"
}
```

#### POST /extract

Extract product information from a PDF receipt.

**Request:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: PDF file with key `file`

**Response:**

```json
{
  "success": true,
  "receipt": {
    "market": "Pingo Doce",
    "branch": "PD PRELADA",
    "products": [
      {
        "market": "Pingo Doce",
        "branch": "PD PRELADA",
        "product_type": "PEIXARIA",
        "product": "TRANCHE SALMÃO UN150",
        "price": 3.69,
        "quantity": 2.0,
        "discount": null,
        "discount2": null
      }
    ]
  }
}
```

### Using with curl

```bash
curl -X POST "http://localhost:8000/extract" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@receipt.pdf"
```

### Using with Python

```python
import requests

url = "http://localhost:8000/extract"
with open("receipt.pdf", "rb") as file:
    response = requests.post(url, files={"file": file})

print(response.json())
```

## Supported Receipt Format

Currently supports Pingo Doce supermarket receipts with the following format:

```
PD [BRANCH_NAME]
[Header Information]
Artigos
[PRODUCT_TYPE]
[Product Lines...]
```

### Product Line Formats

1. **With quantity and total:**

   ```
   C PRODUCT_NAME QUANTITY X PRICE TOTAL
   ```

2. **Simple price (quantity = 1):**

   ```
   E PRODUCT_NAME PRICE
   ```

3. **With weight quantity:**
   ```
   C PRODUCT_NAME WEIGHT X PRICE TOTAL
   ```

### Example Receipt Structure

```
PD PRELADA
Tel.: 226198120
Pingo Doce - Distribuição Alimentar, S.A.
Artigos
PEIXARIA
C TRANCHE SALMÃO UN150 2,000 X 3,69 7,38
PADARIA/PASTELARIA
E PÃO DE LEITE 1,99
FRUTAS E VEGETAIS
C BANANA IMPORTADA 0,645 X 1,25 0,81
```

## Project Structure

```
src/
├── api/
│   └── main.py              # FastAPI application
├── extraction/
│   ├── __init__.py
│   ├── models.py            # Pydantic data models
│   ├── pdf_extractor.py     # PDF text extraction utility
│   └── receipt_parser.py    # Receipt parsing logic
└── tests/
    ├── test_api.py          # API endpoint tests
    ├── test_pdf_extractor.py # PDF extraction tests
    └── test_receipt_parser.py # Receipt parsing tests
```

## Development

### Running Tests

```bash
# Run all tests
pytest src/tests/

# Run specific test file
pytest src/tests/test_receipt_parser.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### API Documentation

When the server is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **pdfplumber**: PDF text extraction
- **Pydantic**: Data validation and serialization
- **uvicorn**: ASGI server
- **pytest**: Testing framework
- **httpx**: HTTP client for testing

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid file type (non-PDF)
- **422 Unprocessable Entity**: Missing or invalid request data
- **500 Internal Server Error**: PDF processing or parsing errors

Error responses include detailed error messages for debugging.

## Deployment

### Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

### GitHub Actions

Pushes to `main` branch automatically deploy to the VPS using GitHub Actions.

#### Required Secrets

Set the following secrets in your GitHub repository:

- `VPS_HOST`: Your VPS IP address or domain
- `VPS_USERNAME`: SSH username
- `VPS_SSH_KEY`: Private SSH key for authentication

#### Deployment Process

The GitHub Actions workflow performs smart deployment:

- Checks if the app is running and healthy
- Backs up the current deployment
- Updates the code
- Rebuilds and restarts the Docker container
- Verifies the deployment with health checks
- Cleans up unused Docker images

#### Manual Deployment

If needed, you can deploy manually:

```bash
cd /home/receipts-data-extractor/receipts-data-extractor
git pull origin main
docker compose down
docker compose up -d --build
```

## Future Enhancements

- Support for additional supermarket chains
- Batch processing of multiple receipts
- Enhanced discount parsing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
