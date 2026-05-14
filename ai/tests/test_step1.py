"""Step 1 tests: config/dependencies/LLM client wiring."""

import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch


def test_embedding_shape():
    from ai.embeddings.model import EmbeddingModel

    vec = EmbeddingModel().encode("test")
    assert vec.shape == (384,)


def test_embedding_normalized():
    from ai.embeddings.model import EmbeddingModel

    vec = EmbeddingModel().encode("test")
    norm = float(np.linalg.norm(vec))
    assert abs(norm - 1.0) < 1e-5


@pytest.mark.asyncio
async def test_openai_generate_with_string_content():
    from ai.llm.openai_client import OpenAIClient

    client = OpenAIClient()
    client._api_key = "sk-test"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "hello"}}]
        }

        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = await client.generate("hi")

    assert result == "hello"


@pytest.mark.asyncio
async def test_health():
    from ai.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
