# ai/runners/clients/perplexity_client.py
"""
Perplexity API Client using OpenAI-compatible REST API.
Implements AIClient interface for Perplexity models.
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

PERPLEXITY_BASE_URL = "https://api.perplexity.ai"


class PerplexityClient(AIClient):
    """
    Perplexity API client for compliance and research review.

    Uses OpenAI-compatible API via the openai SDK.
    Default model: sonar (online, real-time search)

    Pricing (as of 2026):
    - sonar: $1 per 1M input tokens, $1 per 1M output tokens
    - sonar-pro: $3 per 1M input, $15 per 1M output
    """

    COST_PER_1M_INPUT = 1.0
    COST_PER_1M_OUTPUT = 1.0

    def _get_api_key(self) -> Optional[str]:
        return os.getenv('PERPLEXITY_API_KEY')

    def _get_default_model(self) -> str:
        return "sonar"

    def _initialize_client(self):
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=PERPLEXITY_BASE_URL,
        )

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
            raise RateLimitError(f"Perplexity API rate limit exceeded: {e}")
        except OpenAIConnectionError as e:
            raise APIConnectionError(f"Perplexity API connection error: {e}")
        except Exception as e:
            raise APIConnectionError(f"Unexpected error calling Perplexity API: {e}")

    def _extract_content(self, raw_response: Dict[str, Any]) -> str:
        return raw_response.get('content', '')

    def _extract_input_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['input_tokens']

    def _extract_output_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['output_tokens']

    def get_agent_name(self) -> str:
        return "perplexity"

    def get_model_token_limit(self) -> int:
        # sonar models support 127k context
        return 127_000
