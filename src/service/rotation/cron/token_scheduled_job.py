from typing import List

from src.model.api_provider import ApiProvider
from src.model.api_token import ApiToken
from src.service.rotation.rate_checking.impl.open_ai_rate_limit_checker import open_ai_rate_limit_checker
from src.service.rotation.rate_checking.impl.open_router_rate_limit_checker import open_router_rate_limit_checker
from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker
from src.service.rotation.token_service import token_service
from src.util.logger import get_logger

logger = get_logger(__name__)


rate_limit_checker_map: dict[ApiProvider, RateLimitChecker] = {
    ApiProvider.OPEN_AI: open_ai_rate_limit_checker,
    ApiProvider.OPEN_ROUTER: open_router_rate_limit_checker
}


async def unlock_tokens_scheduled_job():
    logger.info("Running scheduled job...")
    locked_tokens: List[ApiToken] = await token_service.get_locked_tokens()

    if not locked_tokens:
        logger.info("No locked tokens found, skipping further processing")
        return

    for locked_token in locked_tokens:
        logger.info(f'Checking token (id={locked_token.token_id}) for potential unlock.')
        rate_limit_checker: RateLimitChecker = rate_limit_checker_map.get(locked_token.api_provider)
        is_token_unlocked: bool = await rate_limit_checker.is_unlocked(locked_token.value)
        if is_token_unlocked:
            logger.info(f'Unlocking token (id={locked_token.token_id}).')
            await token_service.unlock(locked_token.token_id)

    logger.info(f'Scheduled has finished.')
