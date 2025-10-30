from abc import ABC, abstractmethod

import backoff

from src.exception.exception_handler import RetryableException, AiHttpCallException
from src.util.logger import get_logger

logger = get_logger(__name__)


class RotatableService(ABC):

    # ToDo: 03/10 should be configurable
    @backoff.on_exception(backoff.expo, RetryableException, max_tries=3)
    async def _process_with_retry(self, *args, **kwargs):
        try:
            result = await self._process_internal(*args, **kwargs)
            return result
        except AiHttpCallException as e:
            await self._handle_exception(e)

    async def _handle_exception(self, e: AiHttpCallException):
        if self._is_rate_limit_exception(e):
            await self._rotate_api_key()
            raise RetryableException(e)

        if self._is_retryable_exception(e):
            raise RetryableException(e)

        raise e

    @abstractmethod
    async def _process_internal(self, *args, **kwargs):
        pass

    @abstractmethod
    def _is_rate_limit_exception(self, e: AiHttpCallException) -> bool:
        pass

    @abstractmethod
    def _is_retryable_exception(self, e: AiHttpCallException) -> bool:
        pass

    @abstractmethod
    async def _rotate_api_key(self) -> None:
        pass
