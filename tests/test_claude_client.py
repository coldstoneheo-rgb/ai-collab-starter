# tests/test_claude_client.py
"""
Unit tests for Claude API Client.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from ai.runners.clients.claude_client import ClaudeClient
from ai.runners.clients.base_client import (
    APIKeyMissingError,
    RateLimitError,
    APIConnectionError,
)
from ai.utils.models import AIResponse


class TestClaudeClient:
    """Test suite for ClaudeClient."""

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key_123'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_init(self, mock_anthropic):
        """Test initialization."""
        client = ClaudeClient()
        assert client.api_key == 'test_key_123'
        assert client.model == 'claude-sonnet-4-5-20250929'
        assert client.get_agent_name() == 'claude'
        mock_anthropic.assert_called_once_with(api_key='test_key_123')

    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_init_with_explicit_key(self, mock_anthropic):
        """Test initialization with explicit API key."""
        client = ClaudeClient(api_key='explicit_key')
        assert client.api_key == 'explicit_key'
        mock_anthropic.assert_called_once_with(api_key='explicit_key')

    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_missing_api_key(self, mock_anthropic):
        """Test error when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(APIKeyMissingError):
                ClaudeClient()

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_send_prompt(self, mock_anthropic):
        """Test sending a prompt."""
        # Mock response
        mock_response = MagicMock()
        mock_response.id = 'msg_123'
        mock_response.model = 'claude-sonnet-4-5-20250929'
        mock_response.role = 'assistant'
        mock_response.stop_reason = 'end_turn'

        # Mock content
        mock_content_block = MagicMock()
        mock_content_block.text = 'This is a test response'
        mock_content_block.type = 'text'
        mock_response.content = [mock_content_block]

        # Mock usage
        mock_usage = MagicMock()
        mock_usage.input_tokens = 100
        mock_usage.output_tokens = 50
        mock_response.usage = mock_usage

        # Setup client mock
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Test
        client = ClaudeClient()
        response = client.send_prompt("Test prompt")

        # Assertions
        assert isinstance(response, AIResponse)
        assert response.agent == 'claude'
        assert response.model == 'claude-sonnet-4-5-20250929'
        assert response.content == 'This is a test response'
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.total_tokens == 150
        assert response.success is True

        # Verify API call
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs['model'] == 'claude-sonnet-4-5-20250929'
        assert call_kwargs['messages'][0]['content'] == 'Test prompt'

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_cost_calculation(self, mock_anthropic):
        """Test cost calculation for Claude."""
        client = ClaudeClient()

        # Claude Sonnet 4.5 pricing:
        # Input: $3 per 1M tokens
        # Output: $15 per 1M tokens
        cost = client.calculate_cost(1000, 500)
        expected = (1000 / 1_000_000 * 3.0) + (500 / 1_000_000 * 15.0)
        assert cost == pytest.approx(expected, rel=1e-6)

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_token_limit(self, mock_anthropic):
        """Test token limit checking."""
        client = ClaudeClient()

        # Claude Sonnet 4.5 has 200k context window
        assert client.get_model_token_limit() == 200_000

        # Short prompt should be within limit
        short_prompt = "Hello" * 100
        assert client.check_token_limit(short_prompt, 4000) is True

        # Very long prompt should exceed limit
        long_prompt = "a" * 1_000_000  # ~250k tokens
        assert client.check_token_limit(long_prompt, 4000) is False

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_rate_limit_error(self, mock_anthropic):
        """Test handling of rate limit errors."""
        # Test that exceptions are properly wrapped
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()

        # Generic exceptions are wrapped in APIConnectionError
        with pytest.raises(APIConnectionError):
            client.send_prompt("Test")

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_api_error(self, mock_anthropic):
        """Test handling of API errors."""
        # Similar approach - test that errors are properly wrapped
        mock_client = MagicMock()
        mock_exception = Exception("API is overloaded")
        mock_client.messages.create.side_effect = mock_exception
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()

        with pytest.raises(APIConnectionError):
            client.send_prompt("Test")

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_key'})
    @patch('ai.runners.clients.claude_client.Anthropic')
    def test_custom_model(self, mock_anthropic):
        """Test using a custom model."""
        client = ClaudeClient(model='claude-opus-4-5-20251101')
        assert client.model == 'claude-opus-4-5-20251101'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
