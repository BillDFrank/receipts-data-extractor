[![Test API](https://github.com/BillDFrank/receipts-data-extractor/actions/workflows/test-api.yml/badge.svg)](https://github.com/BillDFrank/receipts-data-extractor/actions/workflows/test-api.yml)
# Pingo Receipt Parser API

A robust FastAPI-based service for extracting and parsing product information from Portuguese supermarket receipts, with specialized support for Pingo Doce receipts. Built with modern Python tools for reliable PDF processing and structured data extraction.

## ✨ Features

- **PDF Text Extraction**: Advanced PDF processing using pdfplumber
- **Intelligent Parsing**: Specialized parser for Pingo Doce receipt formats
- **RESTful API**: Clean FastAPI endpoints with automatic OpenAPI documentation
- **Type Safety**: Full Pydantic models for data validation and serialization
- **Docker Ready**: Containerized deployment with Docker Compose
- **Comprehensive Testing**: Full test coverage with pytest
- **Production Ready**: Health checks, error handling, and logging
- **CI/CD Ready**: Automated deployment with GitHub Actions

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

## 🎯 Parsing Capabilities

The parser intelligently extracts:
- **Market & Branch**: Automatic detection of Pingo Doce locations
- **Product Details**: Name, type, quantity, unit price, and total
- **Discounts**: Multiple discount types and amounts
- **Receipt Metadata**: Invoice number, date, and total amount
- **Product Categories**: Organized by department (PEIXARIA, PADARIA, etc.)

### Supported Product Formats
1. **Quantity + Price**: `C PRODUCT_NAME QUANTITY X PRICE TOTAL`
2. **Simple Items**: `E PRODUCT_NAME PRICE`
3. **Weighted Items**: `C PRODUCT_NAME WEIGHT X PRICE TOTAL`
4. **Complex Items**: `E C PRODUCT_NAME QUANTITY PRICE`

## 🏗️ Architecture

The application follows a clean, modular architecture:

```
src/
├── api/
│   └── main.py              # FastAPI application with endpoints
├── extraction/
│   ├── __init__.py
│   ├── models.py            # Pydantic data models and schemas
│   ├── pdf_extractor.py     # PDF text extraction using pdfplumber
│   └── receipt_parser.py    # Specialized Pingo Doce receipt parser
└── tests/
    ├── test_api.py          # API endpoint tests
    ├── test_pdf_extractor.py # PDF extraction tests
    └── test_receipt_parser.py # Receipt parsing tests
```

### Core Components

- **API Layer**: FastAPI with automatic OpenAPI docs and validation
- **Extraction Engine**: PDF processing and text extraction
- **Parsing Engine**: Intelligent receipt parsing with regex patterns
- **Data Models**: Type-safe data structures with Pydantic

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

## 🛠️ Technology Stack

### Core Dependencies
- **FastAPI**: High-performance async web framework
- **pdfplumber**: Robust PDF text extraction library
- **Pydantic v2**: Data validation and serialization with Python type hints
- **uvicorn**: Lightning-fast ASGI server with auto-reload

### Development & Testing
- **pytest**: Comprehensive testing framework
- **httpx**: Async HTTP client for API testing
- **ruff**: Fast Python linter and formatter

### Deployment
- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD pipeline automation

### Python Version
- **Python 3.10+**: Leveraging modern Python features and performance improvements

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid file type (non-PDF)
- **422 Unprocessable Entity**: Missing or invalid request data
- **500 Internal Server Error**: PDF processing or parsing errors

Error responses include detailed error messages for debugging.

## Deployment

### Docker

#### Quick Start
Build and run with Docker Compose:

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env

# Build and run
docker compose up --build
```

The API will be available at `http://localhost:8000`

#### Environment Configuration
The application supports configuration via environment variables:

- Copy `.env.example` to `.env`
- Modify values according to your needs
- The Docker Compose file automatically loads these variables

### GitHub Actions

#### Automated Testing
The project includes comprehensive CI/CD with automated testing:

- **API Testing**: `test-api.yml` - Builds container, starts service, and tests all endpoints
- **Deployment**: `main.yml` - Automated deployment to VPS on main branch pushes

#### Testing Workflow Features
- ✅ Docker image build verification
- ✅ Health endpoint testing
- ✅ API endpoint validation
- ✅ Error handling verification
- ✅ Unit test execution
- ✅ Automatic cleanup

Pushes to `main` branch automatically deploy to the VPS using GitHub Actions.

#### Required Secrets

Set the following secrets in your GitHub repository:

- `VPS_HOST`: Your VPS IP address or domain
- `VPS_USERNAME`: SSH username
- `VPS_SSH_KEY`: Private SSH key for authentication
- `VPS_SSH_PASSPHRASE`: Passphrase for the SSH key (if protected)

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

## 🚀 Future Enhancements

- **Multi-Chain Support**: Extend parsing to other Portuguese supermarkets (Continente, Lidl, etc.)
- **Batch Processing**: Handle multiple receipts in single API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
