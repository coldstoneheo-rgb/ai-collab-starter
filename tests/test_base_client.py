# tests/test_base_client.py
"""
Unit tests for AI Client Base.
"""
import pytest
from unittest.mock import Mock, patch
import time

from ai.runners.clients.base_client import (
    AIClient,
    MockAIClient,
    ClientConfig,
    AIClientError,
    APIKeyMissingError,
    RateLimitError,
    APIConnectionError,
)
from ai.utils.models import AIResponse


class TestClientConfig:
    """Test ClientConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ClientConfig()
        assert config.timeout == 60
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.max_tokens == 4000
        assert config.temperature == 0.7
        assert config.top_p == 1.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ClientConfig(
            timeout=30,
            max_retries=5,
            retry_delay=2.0,
            max_tokens=8000,
        )
        assert config.timeout == 30
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.max_tokens == 8000


class TestMockAIClient:
    """Test MockAIClient."""

    def test_init(self):
        """Test initialization."""
        client = MockAIClient(response_text="Test response")
        assert client.model == "mock-model"
        assert client.api_key == "mock_key"
        assert client.response_text == "Test response"
        assert client.call_count == 0

    def test_send_prompt(self):
        """Test sending a prompt."""
        client = MockAIClient(response_text="Hello, world!")
        response = client.send_prompt("Test prompt")

        assert isinstance(response, AIResponse)
        assert response.agent == "mock"
        assert response.model == "mock-model"
        assert response.content == "Hello, world!"
        assert response.success is True
        assert response.error_message is None
        assert response.input_tokens > 0
        assert response.output_tokens > 0
        assert response.cost_usd == 0.0  # Mock client has zero cost
        assert client.call_count == 1

    def test_multiple_calls(self):
        """Test multiple calls increment counter."""
        client = MockAIClient()

        client.send_prompt("Prompt 1")
        assert client.call_count == 1

        client.send_prompt("Prompt 2")
        assert client.call_count == 2

        client.send_prompt("Prompt 3")
        assert client.call_count == 3


class TestAIClientBase:
    """Test AIClient base functionality using MockAIClient."""

    def test_calculate_cost(self):
        """Test cost calculation."""
        client = MockAIClient()

        # Override cost constants for testing
        client.COST_PER_1M_INPUT = 3.0  # $3 per 1M input tokens
        client.COST_PER_1M_OUTPUT = 15.0  # $15 per 1M output tokens

        # Test with 1000 input tokens and 500 output tokens
        cost = client.calculate_cost(1000, 500)
        expected = (1000 / 1_000_000 * 3.0) + (500 / 1_000_000 * 15.0)
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_estimate_tokens(self):
        """Test token estimation."""
        client = MockAIClient()

        # ~4 characters per token
        text = "a" * 400  # 400 characters
        estimated = client.estimate_tokens(text)
        assert estimated == 100  # 400 / 4

    def test_check_token_limit(self):
        """Test token limit checking."""
        client = MockAIClient()

        # Short prompt should be within limit
        short_prompt = "Hello"
        assert client.check_token_limit(short_prompt, 1000) is True

        # Very long prompt should exceed limit
        long_prompt = "a" * 40000  # ~10k tokens
        assert client.check_token_limit(long_prompt, 5000) is False

    def test_get_cost_estimate(self):
        """Test cost estimation."""
        client = MockAIClient()
        client.COST_PER_1M_INPUT = 3.0
        client.COST_PER_1M_OUTPUT = 15.0

        prompt = "a" * 400  # ~100 tokens
        max_output = 200

        cost = client.get_cost_estimate(prompt, max_output)
        expected = (100 / 1_000_000 * 3.0) + (200 / 1_000_000 * 15.0)
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_repr(self):
        """Test string representation."""
        client = MockAIClient()
        assert repr(client) == "MockAIClient(model=mock-model)"


class TestRetryLogic:
    """Test retry logic and error handling."""

    def test_rate_limit_retry(self):
        """Test retry on rate limit error."""

        class RateLimitClient(MockAIClient):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.attempt_count = 0

            def _send_request(self, prompt: str, **kwargs):
                self.attempt_count += 1
                if self.attempt_count < 2:
                    raise RateLimitError("Rate limit exceeded")
                return super()._send_request(prompt, **kwargs)

        config = ClientConfig(max_retries=3, retry_delay=0.1)
        client = RateLimitClient(config=config)

        start = time.time()
        response = client.send_prompt("Test")
        elapsed = time.time() - start

        assert response.success is True
        assert client.attempt_count == 2
        # Should have waited ~0.1 seconds for retry
        assert elapsed >= 0.1

    def test_connection_error_retry(self):
        """Test retry on connection error."""

        class ConnectionErrorClient(MockAIClient):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.attempt_count = 0

            def _send_request(self, prompt: str, **kwargs):
                self.attempt_count += 1
                if self.attempt_count < 3:
                    raise APIConnectionError("Connection failed")
                return super()._send_request(prompt, **kwargs)

        config = ClientConfig(max_retries=5, retry_delay=0.05)
        client = ConnectionErrorClient(config=config)

        response = client.send_prompt("Test")
        assert response.success is True
        assert client.attempt_count == 3

    def test_max_retries_exceeded(self):
        """Test failure after max retries."""

        class AlwaysFailClient(MockAIClient):
            def _send_request(self, prompt: str, **kwargs):
                raise RateLimitError("Always fails")

        config = ClientConfig(max_retries=2, retry_delay=0.05)
        client = AlwaysFailClient(config=config)

        with pytest.raises(RateLimitError):
            client.send_prompt("Test")

    def test_non_retryable_error(self):
        """Test that non-retryable errors don't retry."""

        class NonRetryableErrorClient(MockAIClient):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.attempt_count = 0

            def _send_request(self, prompt: str, **kwargs):
                self.attempt_count += 1
                raise ValueError("Invalid parameter")

        config = ClientConfig(max_retries=3, retry_delay=0.05)
        client = NonRetryableErrorClient(config=config)

        with pytest.raises(AIClientError):
            client.send_prompt("Test")

        # Should only attempt once (no retries for non-retryable errors)
        assert client.attempt_count == 1


class TestAPIKeyHandling:
    """Test API key handling."""

    def test_missing_api_key(self):
        """Test error when API key is missing."""

        class NoKeyClient(AIClient):
            COST_PER_1M_INPUT = 1.0
            COST_PER_1M_OUTPUT = 1.0

            def _get_api_key(self):
                return None

            def _get_default_model(self):
                return "test-model"

            def _initialize_client(self):
                pass

            def _send_request(self, prompt: str, **kwargs):
                return {}

            def _extract_content(self, raw_response):
                return ""

            def _extract_input_tokens(self, raw_response):
                return 0

            def _extract_output_tokens(self, raw_response):
                return 0

            def get_agent_name(self):
                return "test"

        with pytest.raises(APIKeyMissingError):
            NoKeyClient()

    @patch.dict('os.environ', {'TEST_API_KEY': 'env_key_123'})
    def test_api_key_from_env(self):
        """Test loading API key from environment."""
        import os

        class EnvKeyClient(MockAIClient):
            def __init__(self, **kwargs):
                self.response_text = kwargs.get('response_text', 'Mock response')
                self.call_count = 0
                # Don't pass api_key to super, let it use _get_api_key()
                AIClient.__init__(self, api_key=None, **{k: v for k, v in kwargs.items() if k != 'response_text'})

            def _get_api_key(self):
                return os.environ.get('TEST_API_KEY')

        client = EnvKeyClient()
        assert client.api_key == 'env_key_123'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
