"""
API response validation utilities.
"""
from typing import Dict, Any, Optional
import json


class ResponseValidator:
    """Validates API responses"""

    @staticmethod
    def validate_response(response: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that a response has the expected structure.

        Args:
            response: API response to validate

        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not isinstance(response, dict):
            return False, "Response must be a dictionary"

        # Check for common error fields
        if "error" in response:
            return False, f"API returned error: {response['error']}"

        # Response is valid if it's a non-empty dict without errors
        if len(response) == 0:
            return False, "Response is empty"

        return True, None

    @staticmethod
    def validate_response_structure(
        response: Dict[str, Any],
        expected_fields: list[str]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that response contains expected fields.

        Args:
            response: API response
            expected_fields: List of required field names

        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        missing_fields = []
        for field in expected_fields:
            if field not in response:
                missing_fields.append(field)

        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        return True, None

    @staticmethod
    def extract_text_safely(response: Dict[str, Any]) -> Optional[str]:
        """
        Safely extract text from response, returning None if not found.

        Args:
            response: API response

        Returns:
            Extracted text or None
        """
        # Try common response formats
        try:
            # OpenAI-style
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                if "text" in choice:
                    return choice["text"]

            # Anthropic-style
            if "content" in response:
                content = response["content"]
                if isinstance(content, list) and len(content) > 0:
                    if "text" in content[0]:
                        return content[0]["text"]
                if isinstance(content, str):
                    return content

            # Direct fields
            for field in ["text", "response", "answer", "output"]:
                if field in response:
                    return str(response[field])

            # If nothing found, return None
            return None

        except (KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def is_valid_json(text: str) -> bool:
        """
        Check if text is valid JSON.

        Args:
            text: Text to check

        Returns:
            True if valid JSON, False otherwise
        """
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
