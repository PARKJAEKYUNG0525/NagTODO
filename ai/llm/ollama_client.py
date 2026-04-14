import httpx

from ai.core.config import settings

'''Ollama `/api/generate` 엔드포인트를 호출하는 `OllamaClient` 클래스'''

class OllamaClient:
    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_BASE_URL
        self._model = settings.OLLAMA_MODEL
        self._timeout = settings.OLLAMA_TIMEOUT

    # llm에 프롬프트 전송하고 결과 반환 (비동기)
    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,  # 토큰 스트리밍없이 한 번에 전체 답변 받기
        }
        # 비동기 HTTP 클라이언트 생성 (API 통신용 브라우저 열기)
        # async with : 자동으로 자원 정리
        #              요청 끝나면 connection close, 메모리 정리, 세션 종료
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            return response.json()["response"]
