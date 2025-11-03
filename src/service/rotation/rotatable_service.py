from abc import ABC, abstractmethod

import backoff

from src.exception.exception_handler import RotatableException
from src.util.logger import get_logger

logger = get_logger(__name__)


class RotatableService(ABC):

    def __init__(self, rotation_retry_count: int):
        self._rotation_retry_count = rotation_retry_count

    async def process_with_token_rotation(self, *args, **kwargs):
        async def wrapped():
            return await self._process_with_token_rotation_internal(*args, **kwargs)

        retryable = backoff.on_exception(
            backoff.expo, RotatableException, max_tries=self._rotation_retry_count)(wrapped)
        return await retryable()

    async def _process_with_token_rotation_internal(self, *args, **kwargs):
        try:
            result = await self._process_with_retry(*args, **kwargs)
            return result
        except RotatableException as e:
            await self._handle_exception(e)

    async def _handle_exception(self, e: RotatableException):
        await self._rotate_api_key()
        raise e

    @abstractmethod
    async def _process_with_retry(self, *args, **kwargs):
        pass

    @abstractmethod
    async def _rotate_api_key(self) -> None:
        pass
