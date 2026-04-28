# tests/test_gemini_client.py
"""
Unit tests for Gemini API Client.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

try:
    import google.generativeai  # noqa: F401
except BaseException:
    pytest.skip("google-generativeai not available in this environment", allow_module_level=True)

from ai.runners.clients.gemini_client import GeminiClient
from ai.runners.clients.base_client import APIKeyMissingError, RateLimitError, APIConnectionError


class TestGeminiClient:

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key_123'})
    @patch('ai.runners.clients.gemini_client.genai')
    def test_init(self, mock_genai):
        mock_genai.GenerativeModel.return_value = Mock()
        client = GeminiClient()
        assert client.api_key == 'test_key_123'
        assert client.model == 'gemini-2.0-flash'
        assert client.get_agent_name() == 'gemini'
        mock_genai.configure.assert_called_once_with(api_key='test_key_123')

    @patch('ai.runners.clients.gemini_client.genai')
    def test_missing_api_key(self, mock_genai):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(APIKeyMissingError):
                GeminiClient()

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gemini_client.genai')
    def test_send_prompt(self, mock_genai):
        mock_response = Mock()
        mock_response.text = "UI looks good, consider adding dark mode."
        mock_response.candidates = [Mock(finish_reason="STOP")]
        mock_response.usage_metadata = None

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.types.GenerationConfig = Mock(return_value={})

        client = GeminiClient()
        response = client.send_prompt("Review this UI component.")

        assert response.content == "UI looks good, consider adding dark mode."
        assert response.agent == "gemini"
        assert response.success is True
        assert response.cost_usd >= 0.0

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gemini_client.genai')
    def test_rate_limit_error(self, mock_genai):
        from google.api_core.exceptions import ResourceExhausted
        mock_model = Mock()
        mock_model.generate_content.side_effect = ResourceExhausted("quota exceeded")
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.types.GenerationConfig = Mock(return_value={})

        client = GeminiClient()
        with pytest.raises(RateLimitError):
            client._send_request("test prompt")

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gemini_client.genai')
    def test_cost_calculation(self, mock_genai):
        mock_genai.GenerativeModel.return_value = Mock()
        client = GeminiClient()
        cost = client.calculate_cost(input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == pytest.approx(0.10 + 0.40, rel=1e-3)

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gemini_client.genai')
    def test_token_limit(self, mock_genai):
        mock_genai.GenerativeModel.return_value = Mock()
        client = GeminiClient()
        assert client.get_model_token_limit() == 1_000_000

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('ai.runners.clients.gemini_client.genai')
    def test_usage_metadata_extraction(self, mock_genai):
        mock_meta = Mock()
        mock_meta.prompt_token_count = 100
        mock_meta.candidates_token_count = 50

        mock_response = Mock()
        mock_response.text = "Review complete."
        mock_response.candidates = [Mock(finish_reason="STOP")]
        mock_response.usage_metadata = mock_meta

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.types.GenerationConfig = Mock(return_value={})

        client = GeminiClient()
        raw = client._send_request("test")
        assert raw['usage']['input_tokens'] == 100
        assert raw['usage']['output_tokens'] == 50
