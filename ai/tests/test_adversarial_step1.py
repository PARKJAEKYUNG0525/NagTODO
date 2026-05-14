"""Adversarial tests for Step 1: config and OpenAI client response handling."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.core.config import settings


class TestConfigValidation:
    def test_config_defaults_exist(self):
        assert settings.OPENAI_API_KEY is not None
        assert settings.OPENAI_MODEL
        assert settings.EMBEDDING_MODEL
        assert settings.VECTOR_DIM == 384

    def test_openai_timeout_is_positive(self):
        assert settings.OPENAI_TIMEOUT > 0

    def test_top_k_is_positive(self):
        assert settings.TOP_K_SIMILAR > 0


class TestOpenAIClientResponseHandling:
    @pytest.mark.asyncio
    async def test_generate_missing_choices_raises_value_error(self):
        from ai.llm.openai_client import OpenAIClient

        client = OpenAIClient()
        client._api_key = "sk-test"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"id": "x"}

            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="choices"):
                await client.generate("test")

    @pytest.mark.asyncio
    async def test_generate_invalid_json_response(self):
        from ai.llm.openai_client import OpenAIClient

        client = OpenAIClient()
        client._api_key = "sk-test"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = ValueError("Invalid JSON")

            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError):
                await client.generate("test")
