from __future__ import annotations

import httpx

from ai.core.config import settings


class OpenAIClient:
    def __init__(self) -> None:
        self._api_key = settings.OPENAI_API_KEY
        self._model = settings.OPENAI_MODEL
        self._timeout = settings.OPENAI_TIMEOUT
        self._base_url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, prompt: str) -> str:
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(self._base_url, headers=headers, json=payload)
                response.raise_for_status()
            except httpx.TimeoutException as e:
                raise TimeoutError(f"OpenAI response timeout ({self._timeout}s)") from e
            except httpx.ConnectError as e:
                raise ConnectionError("OpenAI API connection failed") from e
            except httpx.HTTPStatusError as e:
                body = e.response.text[:300]
                raise RuntimeError(f"OpenAI API error ({e.response.status_code}): {body}") from e

        try:
            data = response.json()
        except Exception as e:
            raise ValueError(f"OpenAI response JSON parse failed: {response.text[:200]}") from e

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError(f"OpenAI response has no choices: {data}")

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text")
                    if isinstance(text, str):
                        text_parts.append(text)
            if text_parts:
                return "".join(text_parts)

        raise ValueError(f"OpenAI response has no text content: {data}")
