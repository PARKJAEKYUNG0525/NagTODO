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
            try:
                response = await client.post(
                    f"{self._base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
            except httpx.TimeoutException as e:
                raise TimeoutError(f"Ollama 응답 시간 초과 ({self._timeout}s)") from e
            except httpx.ConnectError as e:
                raise ConnectionError(f"Ollama 서버 연결 실패: {self._base_url}") from e

            try:
                data = response.json()
            except Exception as e:
                raise ValueError(f"Ollama 응답 JSON 파싱 실패: {response.text[:200]}") from e
            if "response" not in data:
                raise ValueError(f"Ollama 응답에 'response' 필드 없음: {data}")
            return data["response"]
