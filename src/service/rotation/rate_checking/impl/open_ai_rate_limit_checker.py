from typing import override

from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker


class OpenAiRateLimitChecker(RateLimitChecker):

    @override
    async def is_unlocked(self, token: str) -> bool:
        # ToDo: 03/10 It's mocked now
        return False


open_ai_rate_limit_checker = OpenAiRateLimitChecker()
