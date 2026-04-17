"""Adversarial tests for Step 1: Config, Dependencies, EmbeddingModel, OllamaClient"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ai.core.config import settings


class TestConfigValidation:
    """Config 설정 값 경계 검증"""

    def test_config_defaults_exist(self):
        """모든 필수 설정이 기본값을 가져야 함"""
        assert settings.OLLAMA_BASE_URL is not None
        assert settings.OLLAMA_MODEL is not None
        assert settings.EMBEDDING_MODEL is not None
        assert settings.VECTOR_DIM == 384
        assert settings.TOP_K_SIMILAR == 20

    def test_vector_dim_matches_embedding_model(self):
        """VECTOR_DIM이 실제 모델 차원과 일치해야 함"""
        assert settings.VECTOR_DIM == 384  # multilingual-e5-small

    def test_ollama_timeout_is_positive(self):
        """Ollama 타임아웃은 양수여야 함"""
        assert settings.OLLAMA_TIMEOUT > 0

    def test_top_k_is_positive(self):
        """TOP_K_SIMILAR은 양수여야 함"""
        assert settings.TOP_K_SIMILAR > 0


class TestOllamaClientResponseHandling:
    """OllamaClient 응답 처리 검증"""

    @pytest.mark.asyncio
    async def test_generate_response_missing_response_field(self):
        """Ollama 응답에서 'response' 필드 누락 시 ValueError 발생"""
        from ai.llm.ollama_client import OllamaClient

        client = OllamaClient()
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"wrong_field": "value"}

            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="response"):
                await client.generate("test")

    @pytest.mark.asyncio
    async def test_generate_invalid_json_response(self):
        """JSON 파싱 실패 시 예외 전파"""
        from ai.llm.ollama_client import OllamaClient

        client = OllamaClient()
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
