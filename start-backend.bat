@echo off
echo Starting ConversationIQ Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install -r requirements-web.txt

REM Initialize database
echo Initializing database...
python -c "from src.storage.database import init_database; init_database()"

REM Start FastAPI server
echo Starting FastAPI server on http://localhost:8000
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
