from typing import override

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

        return resp.status_code < 400


open_router_rate_limit_checker = OpenRouterRateLimitChecker(
    url="https://openrouter.ai/api/v1/chat/completions",
    model="meta-llama/llama-4-scout:free")
