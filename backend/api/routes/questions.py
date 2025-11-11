"""
Question management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import tempfile
import os

from src.tests.questions import QuestionLoader
from src.storage.schemas import QuestionCreate

router = APIRouter()


@router.post("/upload", response_model=List[dict])
async def upload_questions(file: UploadFile = File(...)):
    """Upload a questions file (JSON, CSV, or TXT)"""
    # Save uploaded file temporarily
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # Load questions using auto-detect
        questions = QuestionLoader.auto_detect_format(tmp_file_path)

        # Convert to dict for response
        return [q.model_dump() for q in questions]

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse questions file: {str(e)}")

    finally:
        # Clean up temp file
        os.unlink(tmp_file_path)


@router.post("/parse", response_model=List[dict])
async def parse_questions(questions_text: str, delimiter: str = "\n\n"):
    """Parse questions from text"""
    questions = QuestionLoader.from_list([q.strip() for q in questions_text.split(delimiter) if q.strip()])
    return [q.model_dump() for q in questions]
