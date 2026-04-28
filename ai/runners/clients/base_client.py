# ai/runners/clients/base_client.py
"""
Base Client for AI API integrations.
Defines common interface and utilities for all AI clients.
"""
import time
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from ai.utils.models import AIResponse


@dataclass
class ClientConfig:
    """Configuration for AI clients."""
    timeout: int = 60  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds, exponential backoff
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0


class AIClientError(Exception):
    """Base exception for AI client errors."""
    pass


class APIKeyMissingError(AIClientError):
    """API key is not provided or not found."""
    pass


class RateLimitError(AIClientError):
    """API rate limit exceeded."""
    pass


class TokenLimitError(AIClientError):
    """Token limit exceeded."""
    pass


class APIConnectionError(AIClientError):
    """Failed to connect to API."""
    pass


class AIClient(ABC):
    """
    Abstract base class for AI API clients.
    All AI clients (Claude, Gemini, Perplexity, GPT) must inherit from this.
    """

    # Subclasses must define these cost constants (per 1M tokens)
    COST_PER_1M_INPUT: float = 0.0
    COST_PER_1M_OUTPUT: float = 0.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[ClientConfig] = None
    ):
        """
        Initialize AI client.

        Args:
            api_key: API key for the service
            model: Model name to use
            config: Client configuration
        """
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise APIKeyMissingError(f"API key not provided for {self.__class__.__name__}")

        self.model = model or self._get_default_model()
        self.config = config or ClientConfig()
        self._initialize_client()

    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or other source."""
        pass

    @abstractmethod
    def _get_default_model(self) -> str:
        """Get default model name for this client."""
        pass

    @abstractmethod
    def _initialize_client(self):
        """Initialize the underlying API client (SDK)."""
        pass

    @abstractmethod
    def _send_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send request to AI API.
        This is the core method that subclasses must implement.

        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters

        Returns:
            Raw response dictionary from API
        """
        pass

    def send_prompt(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> AIResponse:
        """
        Send prompt to AI and get response with retry logic.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional parameters

        Returns:
            AIResponse object

        Raises:
            AIClientError: If request fails after all retries
        """
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                # Send request
                raw_response = self._send_request(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                # Parse response
                ai_response = self._parse_response(raw_response)
                return ai_response

            except RateLimitError as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    print(f"⚠️ Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{self.config.max_retries})")
                    time.sleep(delay)
                    continue
                raise

            except APIConnectionError as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    print(f"⚠️ Connection error, retrying in {delay}s (attempt {attempt + 1}/{self.config.max_retries})")
                    time.sleep(delay)
                    continue
                raise

            except Exception as e:
                # Don't retry on other errors
                raise AIClientError(f"Unexpected error: {e}")

        raise AIClientError(f"Failed after {self.config.max_retries} retries: {last_error}")

    def _parse_response(self, raw_response: Dict[str, Any]) -> AIResponse:
        """
        Parse raw API response into AIResponse object.
        Subclasses can override for custom parsing.

        Args:
            raw_response: Raw response from API

        Returns:
            AIResponse object
        """
        content = self._extract_content(raw_response)
        input_tokens = self._extract_input_tokens(raw_response)
        output_tokens = self._extract_output_tokens(raw_response)
        total_tokens = input_tokens + output_tokens

        cost = self.calculate_cost(input_tokens, output_tokens)

        return AIResponse(
            agent=self.get_agent_name(),
            content=content,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            timestamp=datetime.now(),
            success=True,
            error_message=None,
            metadata={'raw_response': raw_response}
        )

    @abstractmethod
    def _extract_content(self, raw_response: Dict[str, Any]) -> str:
        """Extract content text from raw response."""
        pass

    @abstractmethod
    def _extract_input_tokens(self, raw_response: Dict[str, Any]) -> int:
        """Extract input token count from raw response."""
        pass

    @abstractmethod
    def _extract_output_tokens(self, raw_response: Dict[str, Any]) -> int:
        """Extract output token count from raw response."""
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in USD based on token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * self.COST_PER_1M_INPUT
        output_cost = (output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT
        return round(input_cost + output_cost, 6)

    @abstractmethod
    def get_agent_name(self) -> str:
        """Get agent name (claude, gemini, perplexity, gpt)."""
        pass

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        This is a rough approximation: ~4 chars per token.
        Subclasses can override with more accurate tokenization.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def check_token_limit(self, prompt: str, max_tokens: int) -> bool:
        """
        Check if prompt + response will exceed model's token limit.

        Args:
            prompt: The prompt text
            max_tokens: Maximum tokens to generate

        Returns:
            True if within limit, False otherwise
        """
        estimated_prompt_tokens = self.estimate_tokens(prompt)
        total_estimated = estimated_prompt_tokens + max_tokens

        # Most models have 4k-8k context windows, but some have more
        # Subclasses should override this with actual limits
        model_limit = self.get_model_token_limit()

        return total_estimated <= model_limit

    def get_model_token_limit(self) -> int:
        """
        Get model's maximum token limit.
        Subclasses should override with actual limits.

        Returns:
            Token limit for current model
        """
        return 8000  # Conservative default

    def get_cost_estimate(self, prompt: str, max_output_tokens: int) -> float:
        """
        Estimate cost for a request.

        Args:
            prompt: The prompt text
            max_output_tokens: Maximum tokens to generate

        Returns:
            Estimated cost in USD
        """
        input_tokens = self.estimate_tokens(prompt)
        return self.calculate_cost(input_tokens, max_output_tokens)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"


class MockAIClient(AIClient):
    """
    Mock AI client for testing.
    Returns predefined responses without making actual API calls.
    """

    COST_PER_1M_INPUT = 0.0
    COST_PER_1M_OUTPUT = 0.0

    def __init__(self, response_text: str = "Mock response", **kwargs):
        self.response_text = response_text
        self.call_count = 0
        super().__init__(api_key="mock_key", **kwargs)

    def _get_api_key(self) -> str:
        return "mock_key"

    def _get_default_model(self) -> str:
        return "mock-model"

    def _initialize_client(self):
        self.client = None  # No actual client needed

    def _send_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        self.call_count += 1
        return {
            'content': self.response_text,
            'usage': {
                'input_tokens': self.estimate_tokens(prompt),
                'output_tokens': self.estimate_tokens(self.response_text),
            }
        }

    def _extract_content(self, raw_response: Dict[str, Any]) -> str:
        return raw_response['content']

    def _extract_input_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['input_tokens']

    def _extract_output_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['output_tokens']

    def get_agent_name(self) -> str:
        return "mock"
