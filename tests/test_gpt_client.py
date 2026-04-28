# tests/test_gpt_client.py
"""
Unit tests for GPT API Client.
"""
import pytest
from unittest.mock import Mock, patch

pytest.importorskip("openai")

from ai.runners.clients.gpt_client import GPTClient
from ai.runners.clients.base_client import APIKeyMissingError, RateLimitError, APIConnectionError


def _make_mock_response(content="Backend looks solid.", input_tokens=120, output_tokens=60):
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


class TestGPTClient:

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_123'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_init(self, mock_openai):
        mock_openai.return_value = Mock()
        client = GPTClient()
        assert client.api_key == 'test_key_123'
        assert client.model == 'gpt-4o'
        assert client.get_agent_name() == 'gpt'

    @patch.dict('os.environ', {'GPT_API_KEY': 'legacy_key'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_init_legacy_key(self, mock_openai):
        """GPT_API_KEY env var (legacy) should also work."""
        mock_openai.return_value = Mock()
        with patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=False):
            client = GPTClient(api_key='legacy_key')
        assert client.api_key == 'legacy_key'

    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_missing_api_key(self, mock_openai):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(APIKeyMissingError):
                GPTClient()

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_send_prompt(self, mock_openai):
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = _make_mock_response()
        mock_openai.return_value = mock_client

        client = GPTClient()
        response = client.send_prompt("Review backend API design.")

        assert response.content == "Backend looks solid."
        assert response.agent == "gpt"
        assert response.success is True
        assert response.input_tokens == 120
        assert response.output_tokens == 60

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_rate_limit_error(self, mock_openai):
        from openai import RateLimitError as OpenAIRateLimitError
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = OpenAIRateLimitError(
            message="rate limit", response=Mock(status_code=429), body={}
        )
        mock_openai.return_value = mock_client

        client = GPTClient()
        with pytest.raises(RateLimitError):
            client._send_request("test prompt")

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_cost_calculation(self, mock_openai):
        mock_openai.return_value = Mock()
        client = GPTClient()
        cost = client.calculate_cost(input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == pytest.approx(2.50 + 10.0, rel=1e-3)

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_token_limit_gpt4o(self, mock_openai):
        mock_openai.return_value = Mock()
        client = GPTClient(model='gpt-4o')
        assert client.get_model_token_limit() == 128_000

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gpt_client.OpenAI')
    def test_token_limit_default(self, mock_openai):
        mock_openai.return_value = Mock()
        client = GPTClient(model='gpt-3.5-turbo')
        assert client.get_model_token_limit() == 16_000
