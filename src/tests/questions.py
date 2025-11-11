"""
Question management and loading from various formats.
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

import pandas as pd

from ..storage.schemas import QuestionCreate

logger = logging.getLogger(__name__)


class QuestionLoader:
    """Loads questions from various file formats"""

    @staticmethod
    def from_json(file_path: str) -> List[QuestionCreate]:
        """
        Load questions from JSON file.

        JSON format can be:
        - Array of question objects
        - Object with "questions" array

        Args:
            file_path: Path to JSON file

        Returns:
            List of QuestionCreate objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            questions_data = data
        elif isinstance(data, dict) and "questions" in data:
            questions_data = data["questions"]
        else:
            raise ValueError(
                "JSON must be an array of questions or an object with 'questions' array"
            )

        questions = []
        for idx, q_data in enumerate(questions_data):
            try:
                # Ensure text field exists
                if "text" not in q_data and "question" in q_data:
                    q_data["text"] = q_data.pop("question")

                question = QuestionCreate(**q_data)
                questions.append(question)
            except Exception as e:
                logger.warning(f"Skipping question {idx + 1}: {e}")
                continue

        logger.info(f"Loaded {len(questions)} questions from {file_path}")
        return questions

    @staticmethod
    def from_csv(file_path: str) -> List[QuestionCreate]:
        """
        Load questions from CSV file.

        CSV should have at minimum a 'text' or 'question' column.
        Optional columns: category, priority, expected_tone

        Args:
            file_path: Path to CSV file

        Returns:
            List of QuestionCreate objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If CSV format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV: {e}")

        # Check for text column
        text_column = None
        for col in ['text', 'question', 'Question', 'Text']:
            if col in df.columns:
                text_column = col
                break

        if text_column is None:
            raise ValueError("CSV must have a 'text' or 'question' column")

        questions = []
        for idx, row in df.iterrows():
            try:
                q_data = {"text": str(row[text_column])}

                # Add optional fields if present
                if 'category' in row and pd.notna(row['category']):
                    q_data['category'] = str(row['category'])

                if 'priority' in row and pd.notna(row['priority']):
                    try:
                        q_data['priority'] = int(row['priority'])
                    except (ValueError, TypeError):
                        pass

                if 'expected_tone' in row and pd.notna(row['expected_tone']):
                    q_data['expected_tone'] = str(row['expected_tone'])

                # Handle metadata columns (any other columns)
                metadata = {}
                for col in df.columns:
                    if col not in [text_column, 'category', 'priority', 'expected_tone']:
                        if pd.notna(row[col]):
                            metadata[col] = str(row[col])

                if metadata:
                    q_data['meta_data'] = metadata

                question = QuestionCreate(**q_data)
                questions.append(question)
            except Exception as e:
                logger.warning(f"Skipping row {idx + 1}: {e}")
                continue

        logger.info(f"Loaded {len(questions)} questions from {file_path}")
        return questions

    @staticmethod
    def from_text(file_path: str, delimiter: str = "\n\n") -> List[QuestionCreate]:
        """
        Load questions from plain text file.

        Questions are separated by delimiter (default: double newline).

        Args:
            file_path: Path to text file
            delimiter: Question separator

        Returns:
            List of QuestionCreate objects

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by delimiter
        question_texts = content.split(delimiter)

        questions = []
        for idx, text in enumerate(question_texts):
            text = text.strip()
            if not text:
                continue

            try:
                question = QuestionCreate(text=text)
                questions.append(question)
            except Exception as e:
                logger.warning(f"Skipping question {idx + 1}: {e}")
                continue

        logger.info(f"Loaded {len(questions)} questions from {file_path}")
        return questions

    @staticmethod
    def from_list(questions: List[str]) -> List[QuestionCreate]:
        """
        Create questions from a list of strings.

        Args:
            questions: List of question texts

        Returns:
            List of QuestionCreate objects
        """
        return [QuestionCreate(text=q) for q in questions if q.strip()]

    @staticmethod
    def auto_detect_format(file_path: str) -> List[QuestionCreate]:
        """
        Auto-detect file format and load questions.

        Args:
            file_path: Path to file

        Returns:
            List of QuestionCreate objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format cannot be detected or loaded
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix == '.json':
            return QuestionLoader.from_json(file_path)
        elif suffix == '.csv':
            return QuestionLoader.from_csv(file_path)
        elif suffix in ['.txt', '.text']:
            return QuestionLoader.from_text(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                "Supported formats: .json, .csv, .txt"
            )


class QuestionExporter:
    """Exports questions to various formats"""

    @staticmethod
    def to_json(questions: List[QuestionCreate], file_path: str):
        """
        Export questions to JSON file.

        Args:
            questions: List of questions
            file_path: Output file path
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        questions_data = [q.model_dump() for q in questions]

        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"questions": questions_data}, f, indent=2)

        logger.info(f"Exported {len(questions)} questions to {file_path}")

    @staticmethod
    def to_csv(questions: List[QuestionCreate], file_path: str):
        """
        Export questions to CSV file.

        Args:
            questions: List of questions
            file_path: Output file path
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to list of dicts
        rows = []
        for q in questions:
            row = {
                'text': q.text,
                'category': q.category or '',
                'priority': q.priority,
                'expected_tone': q.expected_tone or ''
            }
            # Add metadata fields
            for key, value in q.meta_data.items():
                row[key] = value

            rows.append(row)

        # Write CSV
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(path, index=False)

        logger.info(f"Exported {len(questions)} questions to {file_path}")

    @staticmethod
    def to_text(questions: List[QuestionCreate], file_path: str, delimiter: str = "\n\n"):
        """
        Export questions to plain text file.

        Args:
            questions: List of questions
            file_path: Output file path
            delimiter: Question separator
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        question_texts = [q.text for q in questions]
        content = delimiter.join(question_texts)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Exported {len(questions)} questions to {file_path}")
