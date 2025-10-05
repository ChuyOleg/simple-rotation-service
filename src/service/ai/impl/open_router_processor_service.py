from typing import override

from src.model.ukrainian_event import UkrainianEvent
from src.service.ai.ai_client_factory import AiClientFactory, ai_client_factory, AiClientWithTokenId
from src.service.ai.ai_processor_service import AiProcessorService
from src.service.rotation.token_service import TokenService, token_service
from src.util.logger import get_logger


logger = get_logger(__name__)

class OpenRouterProcessorService(AiProcessorService):

    def __init__(self, api_model: str,
                 token_management_service: TokenService,
                 open_router_client_factory: AiClientFactory):

        super().__init__(api_model, token_management_service)
        self._ai_client_factory = open_router_client_factory
        self._open_router_client = None
        self._active_api_token_id = None

    @override
    async def init_ai_client(self):
        ai_client_and_api_token_id: AiClientWithTokenId = await self._ai_client_factory.get_open_router_client()
        self._open_router_client = ai_client_and_api_token_id.ai_client
        self._active_api_token_id = ai_client_and_api_token_id.token_id

    @override
    def _process_internal(self, system_part, user_part) -> UkrainianEvent:
        response = self._open_router_client.chat.completions.create(
        model=self._api_model,
        messages=[system_part, user_part],
        max_tokens=8048,  # ✅ Correct param name in new SDK
        #     ToDo: Refactor (max_tokens for example, make it method's param, etc)
        #     ToDo: disable "reasoning"
        #     ToDo: explore other options for the request
            )
        logger.info(response)
        return response

    @override
    def _is_rate_limit_exception(self, e: Exception) -> bool:
        message = str(e)
        # Check for HTTP 429 and the expected text
        if "429" in message and "Rate limit exceeded" in message:
            logger.warn(f"Rate limit exceeded for Token (id={self._active_api_token_id})")
            return True

        return False

    @override
    async def _rotate_api_key(self) -> None:
        logger.info(f"Rotating OpenRouter API key (token_id: {self._active_api_token_id}).")
        await self._open_router_client.close()
        await self._token_service.lock(self._active_api_token_id)
        await self.init_ai_client()
        logger.info(f"OpenRouter API key has been rotated (new token_id: {self._active_api_token_id}).")


# model='deepseek/deepseek-r1:free'
# model='deepseek/deepseek-chat-v3.1:free'
open_router_processor_service: AiProcessorService = OpenRouterProcessorService(
    api_model='deepseek/deepseek-r1:free',
    token_management_service=token_service,
    open_router_client_factory=ai_client_factory)
