from abc import ABC
from typing import override

import backoff
import httpx

from src.exception.exception_handler import NotFoundTokenException, AiHttpCallRetryableException, RotatableException
from src.model.api_provider import ApiProvider
from src.model.api_token import ApiToken
from src.model.event import create_system_message_prompt, create_user_message_prompt
from src.model.ukrainian_event import UkrainianEvent
from src.repository.ai_api_error_repository import AiApiErrorsRepository
from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker
from src.service.rotation.rotatable_service import RotatableService
from src.service.rotation.token_service import TokenService
from src.util.logger import get_logger

logger = get_logger(__name__)


class AiProcessorService(RotatableService, ABC):

    def __init__(self, api_provider: ApiProvider, base_url: str,
                 http_call_retry_count: int, rotation_retry_count: int,
                 ai_api_errors_repository: AiApiErrorsRepository, token_service: TokenService,
                 rate_limit_checker: RateLimitChecker):
        super().__init__(rotation_retry_count=rotation_retry_count)
        self._api_provider = api_provider
        self._base_url = base_url
        self._http_call_retry_count = http_call_retry_count
        self._ai_api_errors_repository = ai_api_errors_repository
        self._token_service = token_service
        self._rate_limit_checker = rate_limit_checker
        self._api_key = None
        self._active_api_token_id = None

    async def process(self, model: str, raw_event: str) -> UkrainianEvent | None:
        system_part: dict[str, str] = create_system_message_prompt()
        user_part: dict[str, str] = create_user_message_prompt(raw_event)

        processed_event = await self.process_with_token_rotation(model, system_part, user_part)
        return processed_event

    @override
    async def _process_with_retry(self, model, system_part, user_part) -> UkrainianEvent:
        async def wrapped():
            return await self._process_with_retry_internal(model, system_part, user_part)

        retryable = backoff.on_exception(
            backoff.expo, AiHttpCallRetryableException, max_tries=self._http_call_retry_count)(wrapped)
        return await retryable()

    async def _process_with_retry_internal(self, model, system_part, user_part):
        if self._api_key is None:
            await self._rotate_api_key()

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [system_part, user_part],
            "max_tokens": 4048,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload)

            response.raise_for_status()

            response_json = response.json()
            return response_json
        except Exception as e:
            response_json = response.json()
            await self._ai_api_errors_repository.save_error(str(response_json), model)
            if self._rate_limit_checker.is_rate_limit_exception(response_json):
                logger.warn(f"Rate limit exceeded for Token (id={self._active_api_token_id})")
                raise RotatableException(response_json, e)
            raise AiHttpCallRetryableException(response_json, e)

    # ToDo: 19/10 What the behaviour when parallel threads call this method.
    @override
    async def _rotate_api_key(self) -> None:
        if self._api_key is not None:
            await self._token_service.lock(self._active_api_token_id)

        api_token: ApiToken = await self._token_service.get_random_by_api_provider(self._api_provider)
        if api_token is None:
            self._api_key = None
            self._active_api_token_id = -1
            raise NotFoundTokenException(f"No API key found for {self._api_provider} in DB.")

        self._api_key = api_token.value
        self._active_api_token_id = api_token.token_id

        logger.info(f"{self._api_provider} API key has been rotated (new token_id: {self._active_api_token_id}).")
