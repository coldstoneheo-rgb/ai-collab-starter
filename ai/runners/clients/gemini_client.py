# ai/runners/clients/gemini_client.py
"""
Gemini API Client using Google GenerativeAI SDK.
Implements AIClient interface for Gemini models.
"""
import os
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
except ImportError:
    raise ImportError(
        "google-generativeai package not installed. "
        "Install with: pip install google-generativeai>=0.3.0"
    )

from ai.runners.clients.base_client import (
    AIClient,
    ClientConfig,
    RateLimitError,
    APIConnectionError,
)


class GeminiClient(AIClient):
    """
    Gemini API client for UI/UX and multi-perspective review.

    Uses Google's GenerativeAI SDK.
    Default model: gemini-2.0-flash

    Pricing (as of 2026):
    - Input: $0.075 per 1M tokens (≤128k), $0.15 per 1M (>128k)
    - Output: $0.30 per 1M tokens (≤128k), $0.60 per 1M (>128k)
    Using blended average for simplicity.
    """

    COST_PER_1M_INPUT = 0.10
    COST_PER_1M_OUTPUT = 0.40

    def _get_api_key(self) -> Optional[str]:
        return os.getenv('GEMINI_API_KEY')

    def _get_default_model(self) -> str:
        return "gemini-2.0-flash"

    def _initialize_client(self):
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
            }
        )

    def _send_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
            temperature = kwargs.get('temperature', self.config.temperature)

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )

            response = self.client.generate_content(
                prompt,
                generation_config=generation_config,
            )

            input_tokens = self.estimate_tokens(prompt)
            output_tokens = self.estimate_tokens(response.text) if response.text else 0

            # Use usage_metadata if available (more accurate)
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                meta = response.usage_metadata
                if hasattr(meta, 'prompt_token_count'):
                    input_tokens = meta.prompt_token_count
                if hasattr(meta, 'candidates_token_count'):
                    output_tokens = meta.candidates_token_count

            return {
                'text': response.text or '',
                'usage': {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                },
                'finish_reason': str(response.candidates[0].finish_reason) if response.candidates else 'STOP',
            }

        except ResourceExhausted as e:
            raise RateLimitError(f"Gemini API rate limit exceeded: {e}")
        except ServiceUnavailable as e:
            raise APIConnectionError(f"Gemini API unavailable: {e}")
        except Exception as e:
            raise APIConnectionError(f"Unexpected error calling Gemini API: {e}")

    def _extract_content(self, raw_response: Dict[str, Any]) -> str:
        return raw_response.get('text', '')

    def _extract_input_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['input_tokens']

    def _extract_output_tokens(self, raw_response: Dict[str, Any]) -> int:
        return raw_response['usage']['output_tokens']

    def get_agent_name(self) -> str:
        return "gemini"

    def get_model_token_limit(self) -> int:
        # gemini-2.0-flash has 1M token context window
        return 1_000_000
