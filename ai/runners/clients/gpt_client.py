# ai/runners/clients/gpt_client.py
"""
GPT API Client using OpenAI SDK.
Implements AIClient interface for GPT models.
"""
import os
from typing import Optional, Dict, Any

try:
    from openai import OpenAI, RateLimitError as OpenAIRateLimitError, APIConnectionError as OpenAIConnectionError
except ImportError:
    raise ImportError(
        "openai package not installed. "
        "Install with: pip install openai>=1.0.0"
    )

from ai.runners.clients.base_client import (
    AIClient,
    ClientConfig,
    RateLimitError,
    APIConnectionError,
)


class GPTClient(AIClient):
    """
    GPT API client for backend, documentation, and infrastructure review.

    Uses OpenAI's official SDK.
    Default model: gpt-4o

    Pricing (as of 2026):
    - gpt-4o: $2.50 per 1M input tokens, $10 per 1M output tokens
    - gpt-4o-mini: $0.15 per 1M input, $0.60 per 1M output
    """

    COST_PER_1M_INPUT = 2.50
    COST_PER_1M_OUTPUT = 10.0

    def _get_api_key(self) -> Optional[str]:
        return os.getenv('OPENAI_API_KEY') or os.getenv('GPT_API_KEY')

    def _get_default_model(self) -> str:
        return "gpt-4o"

    def _initialize_client(self):
        self.client = OpenAI(api_key=self.api_key)

    def _send_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
            temperature = kwargs.get('temperature', self.config.temperature)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            choice = response.choices[0]
            content = choice.message.content or ''

            input_tokens = response.usage.prompt_tokens if response.usage else self.estimate_tokens(prompt)
            output_tokens = response.usage.completion_tokens if response.usage else self.estimate_tokens(content)

            return {
                'content': content,
                'usage': {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                },
                'finish_reason': choice.finish_reason or 'stop',
            }

        except OpenAIRateLimitError as e:
            raise RateLimitError(f"OpenAI API rate limit exceeded: {e}")
        except OpenAIConnectionError as e:
            raise APIConnectionError(f"OpenAI API connection error: {e}")
        except Exception as e:
            raise APIConnectionError(f"Unexpected error calling OpenAI API: {e}")

    def _extract_content(self, raw_response: Dict[str, Any]) -> str:
        return raw_response.get('content', '')

    def _extract_input_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['input_tokens']

    def _extract_output_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['output_tokens']

    def get_agent_name(self) -> str:
        return "gpt"

    def get_model_token_limit(self) -> int:
        # gpt-4o has 128k context window
        if "gpt-4" in self.model.lower():
            return 128_000
        return 16_000
