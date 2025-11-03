from abc import ABC, abstractmethod
from typing import Any


class RateLimitChecker(ABC):

    @abstractmethod
    def is_rate_limit_exception(self, http_response_json: Any) -> bool:
        pass

    @abstractmethod
    async def is_unlocked(self, token: str) -> bool:
        pass
