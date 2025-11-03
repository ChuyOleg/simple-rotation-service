from typing import override, Any

import httpx

from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker
from src.util.logger import get_logger


logger = get_logger(__name__)

class OpenRouterRateLimitChecker(RateLimitChecker):

    def __init__(self, url: str, model: str):
        self._httpx_limits = httpx.Limits(max_connections=1, max_keepalive_connections=1)
        self._url = url
        self._model = model

    @override
    def is_rate_limit_exception(self, response_json: Any) -> bool:
        error: dict = response_json.get("error", {}) if isinstance(response_json, dict) else {}
        code: int = error.get("code")
        message: str = str(error)

        if 429 == code and "Rate limit exceeded" in message:
            return True

        return False

    @override
    async def is_unlocked(self, token: str) -> bool:
        headers = {
            "Authorization": f"Bearer {token}",
        }

        async with httpx.AsyncClient(limits=self._httpx_limits) as client:
            resp = await client.post(
                self._url,
                headers=headers,
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": "Are you healthy?"}],
                }
            )

        response_json = resp.json()

        _is_rate_limit_exception: bool = self.is_rate_limit_exception(response_json)
        return not _is_rate_limit_exception


open_router_rate_limit_checker = OpenRouterRateLimitChecker(
    url="https://openrouter.ai/api/v1/chat/completions",
    model="meta-llama/llama-4-scout:free")
