from typing import override, Any

from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker


class OpenAiRateLimitChecker(RateLimitChecker):

    @override
    def is_rate_limit_exception(self, http_response_json: Any) -> bool:
        # ToDo: 03/11 It's mocked now
        pass

    @override
    async def is_unlocked(self, token: str) -> bool:
        # ToDo: 03/10 It's mocked now
        return False


open_ai_rate_limit_checker = OpenAiRateLimitChecker()
