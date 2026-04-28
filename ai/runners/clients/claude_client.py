# ai/runners/clients/claude_client.py
"""
Claude API Client using Anthropic SDK.
Implements AIClient interface for Claude models.
"""
import os
from typing import Optional, Dict, Any

try:
    from anthropic import Anthropic, APIError, RateLimitError as AnthropicRateLimitError
except ImportError:
    raise ImportError("anthropic package not installed. Install with: pip install anthropic>=0.18.0")

from ai.runners.clients.base_client import (
    AIClient,
    ClientConfig,
    RateLimitError,
    APIConnectionError,
    TokenLimitError,
)


class ClaudeClient(AIClient):
    """
    Claude API client for code review.

    Uses Anthropic's official SDK to interact with Claude models.
    Default model: claude-sonnet-4-5-20250929

    Pricing (as of 2026-01):
    - Input: $3 per 1M tokens
    - Output: $15 per 1M tokens
    """

    # Cost constants (USD per 1M tokens)
    COST_PER_1M_INPUT = 3.0
    COST_PER_1M_OUTPUT = 15.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[ClientConfig] = None
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (default: CLAUDE_API_KEY env var)
            model: Model name (default: claude-sonnet-4-5-20250929)
            config: Client configuration
        """
        super().__init__(api_key=api_key, model=model, config=config)

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variable."""
        return os.getenv('CLAUDE_API_KEY')

    def _get_default_model(self) -> str:
        """Get default Claude model."""
        return "claude-sonnet-4-5-20250929"

    def _initialize_client(self):
        """Initialize Anthropic SDK client."""
        self.client = Anthropic(api_key=self.api_key)

    def _send_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send request to Claude API.

        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            Raw response from Anthropic API

        Raises:
            RateLimitError: If rate limit is exceeded
            APIConnectionError: If connection fails
            TokenLimitError: If token limit is exceeded
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Convert to dict for consistent handling
            return {
                'id': response.id,
                'model': response.model,
                'role': response.role,
                'content': response.content,
                'stop_reason': response.stop_reason,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                }
            }

        except AnthropicRateLimitError as e:
            raise RateLimitError(f"Claude API rate limit exceeded: {e}")

        except APIError as e:
            if "overloaded" in str(e).lower():
                raise APIConnectionError(f"Claude API is overloaded: {e}")
            elif "timeout" in str(e).lower():
                raise APIConnectionError(f"Claude API timeout: {e}")
            else:
                raise APIConnectionError(f"Claude API error: {e}")

        except Exception as e:
            raise APIConnectionError(f"Unexpected error calling Claude API: {e}")

    def _extract_content(self, raw_response: Dict[str, Any]) -> str:
        """
        Extract text content from Claude response.

        Args:
            raw_response: Raw API response

        Returns:
            Text content
        """
        content_blocks = raw_response['content']

        # Claude returns list of content blocks
        # Usually just one text block, but can be multiple
        text_parts = []
        for block in content_blocks:
            if hasattr(block, 'text'):
                text_parts.append(block.text)
            elif isinstance(block, dict) and 'text' in block:
                text_parts.append(block['text'])
            elif hasattr(block, 'type') and block.type == 'text':
                text_parts.append(block.text)

        return "\n".join(text_parts)

    def _extract_input_tokens(self, raw_response: Dict[str, Any]) -> int:
        """Extract input token count from response."""
        return raw_response['usage']['input_tokens']

    def _extract_output_tokens(self, raw_response: Dict[str, Any]) -> int:
        """Extract output token count from response."""
        return raw_response['usage']['output_tokens']

    def get_agent_name(self) -> str:
        """Get agent name."""
        return "claude"

    def get_model_token_limit(self) -> int:
        """
        Get Claude model's context window size.

        Returns:
            Token limit (200k for Claude Sonnet 4.5)
        """
        # Claude Sonnet 4.5 has 200k context window
        if "sonnet" in self.model.lower() or "opus" in self.model.lower():
            return 200_000
        return 100_000  # Conservative default

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Claude uses similar tokenization to GPT models.
        Rough approximation: ~4 characters per token.

        For more accurate counting, use:
        https://docs.anthropic.com/claude/docs/models-overview#token-counting

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 chars per token
        # This is conservative (slightly overestimates)
        return len(text) // 4
