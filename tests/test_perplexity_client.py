# tests/test_perplexity_client.py
"""
Unit tests for Perplexity API Client.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

pytest.importorskip("openai")

from ai.runners.clients.perplexity_client import PerplexityClient
from ai.runners.clients.base_client import APIKeyMissingError, RateLimitError, APIConnectionError


def _make_mock_response(content="Compliance looks good.", input_tokens=100, output_tokens=50):
    mock_usage = Mock()
    mock_usage.prompt_tokens = input_tokens
    mock_usage.completion_tokens = output_tokens

    mock_message = Mock()
    mock_message.content = content

    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"

    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    return mock_response


class TestPerplexityClient:

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key_123'})
    @patch('ai.runners.clients.perplexity_client.OpenAI')
    def test_init(self, mock_openai):
        mock_openai.return_value = Mock()
        client = PerplexityClient()
        assert client.api_key == 'test_key_123'
        assert client.model == 'sonar'
        assert client.get_agent_name() == 'perplexity'
        mock_openai.assert_called_once()

    @patch('ai.runners.clients.perplexity_client.OpenAI')
    def test_missing_api_key(self, mock_openai):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(APIKeyMissingError):
                PerplexityClient()

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key'})
    @patch('ai.runners.clients.perplexity_client.OpenAI')
    def test_send_prompt(self, mock_openai):
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = _make_mock_response()
        mock_openai.return_value = mock_client

        client = PerplexityClient()
        response = client.send_prompt("Check regulatory compliance.")

        assert response.content == "Compliance looks good."
        assert response.agent == "perplexity"
        assert response.success is True
        assert response.input_tokens == 100
        assert response.output_tokens == 50

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key'})
    @patch('ai.runners.clients.perplexity_client.OpenAI')
    def test_rate_limit_error(self, mock_openai):
        from openai import RateLimitError as OpenAIRateLimitError
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = OpenAIRateLimitError(
            message="rate limit", response=Mock(status_code=429), body={}
        )
        mock_openai.return_value = mock_client

        client = PerplexityClient()
        with pytest.raises(RateLimitError):
            client._send_request("test prompt")

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key'})
    @patch('ai.runners.clients.perplexity_client.OpenAI')
    def test_cost_calculation(self, mock_openai):
        mock_openai.return_value = Mock()
        client = PerplexityClient()
        cost = client.calculate_cost(input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == pytest.approx(1.0 + 1.0, rel=1e-3)

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key'})
    @patch('ai.runners.clients.perplexity_client.OpenAI')
    def test_token_limit(self, mock_openai):
        mock_openai.return_value = Mock()
        client = PerplexityClient()
        assert client.get_model_token_limit() == 127_000
