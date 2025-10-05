from abc import ABC, abstractmethod


class RateLimitChecker(ABC):

    @abstractmethod
    async def is_unlocked(self, token: str) -> bool:
        pass