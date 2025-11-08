#!/bin/bash
# Azure Web App startup script for FastAPI application

# Install dependencies
python -m pip install --upgrade pip
pip install -e .

# Start the FastAPI application using Gunicorn with Uvicorn workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app --bind=0.0.0.0:8000 --timeout 600
