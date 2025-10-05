from abc import ABC, abstractmethod

import backoff

from src.exception.exception_handler import RetryableException, InternalException
from src.util.logger import get_logger

logger = get_logger(__name__)


class RotatableService(ABC):

    # ToDo: 03/10 should be configurable
    @backoff.on_exception(backoff.expo, RetryableException, max_tries=3)
    async def _process_with_retry(self):
        try:
            result = await self._process_internal()
            return result
        except Exception as e:
            await self._handle_exception(e)

    async def _handle_exception(self, e: Exception):
        logger.error(e)
        if self._is_rate_limit_exception(e):
            await self._rotate_api_key()
            raise RetryableException(e)

        raise InternalException(e)

    @abstractmethod
    async def _process_internal(self, *args, **kwargs):
        pass

    @abstractmethod
    def _is_rate_limit_exception(self, e: Exception) -> bool:
        pass

    @abstractmethod
    async def _rotate_api_key(self) -> None:
        pass
