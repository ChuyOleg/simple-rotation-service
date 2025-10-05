from typing import override

from src.exception.exception_handler import InternalException
from src.model.ukrainian_event import UkrainianEvent
from src.service.ai.ai_client_factory import AiClientFactory, ai_client_factory, AiClientWithTokenId
from src.service.ai.ai_processor_service import AiProcessorService
from src.service.rotation.token_service import TokenService, token_service
from src.util.logger import get_logger


logger = get_logger(__name__)

class OpenAIProcessorService(AiProcessorService):

    def __init__(self, api_model: str,
                 token_management_service: TokenService,
                 open_ai_client_factory: AiClientFactory):

        super().__init__(api_model, token_management_service)
        self._ai_client_factory = open_ai_client_factory
        self._open_ai_client = None
        self._active_api_token_id = None

    @override
    async def init_ai_client(self):
        ai_client_and_api_token_id: AiClientWithTokenId = await self._ai_client_factory.get_open_ai_client()
        self._open_ai_client = ai_client_and_api_token_id.ai_client
        self._active_api_token_id = ai_client_and_api_token_id.token_id

    @override
    async def _process_internal(self, system_part, user_part) -> UkrainianEvent:
        try:
            response = await self._open_ai_client.chat.completions.create(
                model=self._api_model,
                messages=[system_part, user_part],
                max_tokens=4048,  # ✅ Correct param name in new SDK
                extra_body={"prompt_cache_key": "DogHotelCacheKey"}  # 👈 non-standard param via `extra_body`
                #     ToDo: Refactor (max_tokens for example, make it method's param, etc)
                #     ToDo: explore other options for the request
            )
            logger.info(response)
            return response
        except Exception as e:
            logger.error(e)
            raise InternalException(e)

    @override
    def _is_rate_limit_exception(self, e: Exception) -> bool:
        # ToDo: 01/10 Mocked now, add real implementation
        return True

    @override
    async def _rotate_api_key(self) -> None:
        logger.info(f"Rotating OpenAI API key (token_id: {self._active_api_token_id}).")
        await self._open_ai_client.close()
        await self._token_service.lock(self._active_api_token_id)
        await self.init_ai_client()
        logger.info("OpenAI API key has been rotated (new token_id: {self._active_api_token_id}).")


open_ai_processor_service: AiProcessorService = OpenAIProcessorService(
    api_model="gpt-4.1-nano",
    token_management_service=token_service,
    open_ai_client_factory=ai_client_factory)
