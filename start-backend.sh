#!/bin/bash

echo "🚀 Starting ConversationIQ Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-web.txt

# Initialize database
echo "Initializing database..."
python -c "from src.storage.database import init_database; init_database()"

# Start FastAPI server
echo "Starting FastAPI server on http://localhost:8000"
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
