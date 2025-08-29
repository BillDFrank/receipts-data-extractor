#!/usr/bin/env python3
"""Main entry point for the Supermarket Receipt Extractor API."""

import uvicorn
from src.api.main import app


def main():
    """Run the FastAPI application."""
    print("Starting Supermarket Receipt Extractor API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
