"""
Generic chat API client for making requests to various chat endpoints.
"""
import httpx
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ChatAPIError(Exception):
    """Exception raised for chat API errors"""
    pass


class ChatAPIClient:
    """
    Generic client for interacting with chat APIs.
    Supports various chat API providers through configuration.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ):
        """
        Initialize chat API client.

        Args:
            endpoint: API endpoint URL
            api_key: API authentication key
            headers: Additional HTTP headers
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.headers = headers or {}
        self.timeout = timeout

        # Add authorization header if not already present
        if "Authorization" not in self.headers and "authorization" not in self.headers:
            self.headers["Authorization"] = f"Bearer {api_key}"

        # Ensure content type is set
        if "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "application/json"

    def send_message(
        self,
        message: str,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a message to the chat API and get response.

        Args:
            message: The message/question to send
            context: Additional context for the chat API
            **kwargs: Additional parameters to pass to the API

        Returns:
            Dict containing the API response

        Raises:
            ChatAPIError: If the API request fails
        """
        try:
            payload = self._build_payload(message, context, **kwargs)

            logger.info(f"Sending request to {self.endpoint}")
            logger.debug(f"Payload: {payload}")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.endpoint,
                    json=payload,
                    headers=self.headers
                )

                response.raise_for_status()
                result = response.json()

                logger.info("Request successful")
                logger.debug(f"Response: {result}")

                return result

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise ChatAPIError(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Request error occurred: {str(e)}"
            logger.error(error_msg)
            raise ChatAPIError(error_msg) from e

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse API response as JSON: {str(e)}"
            logger.error(error_msg)
            raise ChatAPIError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error occurred: {str(e)}"
            logger.error(error_msg)
            raise ChatAPIError(error_msg) from e

    def _build_payload(
        self,
        message: str,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build the request payload for the chat API.
        Can be overridden for specific API formats.

        Args:
            message: The message to send
            context: Additional context
            **kwargs: Additional parameters

        Returns:
            Dict containing the request payload
        """
        # Default payload structure (works for many APIs)
        payload = {
            "messages": [
                {"role": "user", "content": message}
            ],
            **kwargs
        }

        # If context is provided, add it as a system message
        if context:
            payload["messages"].insert(0, {
                "role": "system",
                "content": context
            })

        return payload

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the API connection with a simple message.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            test_message = "Hello, this is a test message."
            response = self.send_message(test_message)
            return True, "Connection successful"
        except ChatAPIError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def extract_response_text(self, response: Dict[str, Any]) -> str:
        """
        Extract the text response from the API response.
        Handles common response formats.

        Args:
            response: The API response dict

        Returns:
            The extracted response text

        Raises:
            ChatAPIError: If response text cannot be extracted
        """
        # Try common response formats
        try:
            # OpenAI-style format
            if "choices" in response:
                return response["choices"][0]["message"]["content"]

            # Anthropic-style format
            if "content" in response:
                if isinstance(response["content"], list):
                    return response["content"][0]["text"]
                return response["content"]

            # Direct text response
            if "text" in response:
                return response["text"]

            # Direct response field
            if "response" in response:
                return response["response"]

            # If we can't find standard fields, return the whole response as string
            logger.warning("Could not find standard response fields, returning full response")
            return json.dumps(response)

        except (KeyError, IndexError, TypeError) as e:
            error_msg = f"Failed to extract response text: {str(e)}"
            logger.error(error_msg)
            raise ChatAPIError(error_msg) from e


class OpenAIChatClient(ChatAPIClient):
    """Specialized client for OpenAI-compatible APIs"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        endpoint = kwargs.pop("endpoint", "https://api.openai.com/v1/chat/completions")
        super().__init__(endpoint=endpoint, api_key=api_key, **kwargs)
        self.model = model

    def _build_payload(self, message: str, context: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        payload = super()._build_payload(message, context, **kwargs)
        payload["model"] = kwargs.get("model", self.model)
        return payload


class AnthropicChatClient(ChatAPIClient):
    """Specialized client for Anthropic Claude API"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        endpoint = kwargs.pop("endpoint", "https://api.anthropic.com/v1/messages")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        super().__init__(endpoint=endpoint, api_key=api_key, headers=headers, **kwargs)
        self.model = model

    def _build_payload(self, message: str, context: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        payload = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "messages": [{"role": "user", "content": message}]
        }

        if context:
            payload["system"] = context

        return payload
