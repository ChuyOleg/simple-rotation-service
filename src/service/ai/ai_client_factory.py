from openai import AsyncOpenAI

from src.model.api_provider import ApiProvider
from src.model.api_token import ApiToken
from src.service.rotation.token_service import TokenService, token_service


class AiClientWithTokenId:
    def __init__(self, ai_client: AsyncOpenAI, token_id: int):
        self.ai_client = ai_client
        self.token_id = token_id

class AiClientFactory:

    def __init__(self, token_management_service: TokenService):
        self._token_service = token_management_service

    async def get_open_ai_client(self) -> AiClientWithTokenId:
        api_token: ApiToken = await self._token_service.get_random_by_api_provider(ApiProvider.OPEN_AI)
        ai_client: AsyncOpenAI = AsyncOpenAI(
            api_key=api_token.value,
            base_url="https://api.openai.com/v1")

        return AiClientWithTokenId(ai_client, api_token.token_id)

    async def get_open_router_client(self) -> AiClientWithTokenId:
        api_token: ApiToken = await self._token_service.get_random_by_api_provider(ApiProvider.OPEN_ROUTER)
        ai_client: AsyncOpenAI = AsyncOpenAI(
            api_key=api_token.value,
            base_url="https://openrouter.ai/api/v1")

        return AiClientWithTokenId(ai_client, api_token.token_id)


ai_client_factory: AiClientFactory = AiClientFactory(token_management_service=token_service)
