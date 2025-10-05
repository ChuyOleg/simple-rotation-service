from typing import Dict, Optional, Any, List

from src.mapping.api_token_mapper import map_api_token_dict_to_api_token
from src.model.api_provider import ApiProvider
from src.model.api_token import ApiToken
from src.repository.token_repository import TokenRepository, token_repository
from src.service.rotation.token_encryptor import token_encryptor, TokenEncryptor
from src.util.logger import get_logger


logger = get_logger(__name__)

class TokenService:

    def __init__(self, repository: TokenRepository, encryptor: TokenEncryptor) -> None:
        self._repository = repository
        self._encryptor = encryptor

    async def get_by_id(self, token_id: int) -> ApiToken:
        token_info: Optional[Dict[str, Any]] = await self._repository.get_by_id(token_id)

        if token_info is None:
            logger.warning(f"Token not found for id={token_id}")
            return ApiToken(token_id=0, api_provider=ApiProvider.UNKNOWN, value='dummyToken')

        token_value = self._encryptor.decrypt(token_info['token_encrypted'])
        return map_api_token_dict_to_api_token(token_info, token_value)

    async def get_random_by_api_provider(self, api_provider: ApiProvider) -> ApiToken:
        token_info: Optional[Dict[str, Any]] = await self._repository.get_random_by_api_provider(api_provider)

        if token_info is None:
            logger.warning(f"Token not found for {api_provider}")
            return ApiToken(token_id=0, api_provider=ApiProvider.UNKNOWN, value='dummyToken')

        token_value = self._encryptor.decrypt(token_info['token_encrypted'])
        return map_api_token_dict_to_api_token(token_info, token_value)

    async def get_locked_tokens(self) -> List[ApiToken]:
        locked_tokens_info: List[Dict[str, Any]] = await self._repository.get_locked_tokens()

        if not locked_tokens_info:
            logger.info(f"No locked tokens found.")
            return []

        return [
            map_api_token_dict_to_api_token(token_info, self._encryptor.decrypt(token_info["token_encrypted"]))
            for token_info in locked_tokens_info]

    async def save(self, token: str, api_provider: ApiProvider) -> Optional[int]:
        encrypted_token: str = self._encryptor.encrypt(token)
        hashed_token: str = self._encryptor.hash(token)

        return await self._repository.save_token(encrypted_token, hashed_token, api_provider)

    async def rotate(self, token_id: int, api_provider: ApiProvider) -> str:
        await self.lock(token_id)
        rotated_token: ApiToken = await self.get_random_by_api_provider(api_provider)
        return rotated_token.value

    async def lock(self, token_id: int):
        success = await self._repository.lock_token(token_id)
        if success:
            logger.info(f"Token [id={token_id}] locked successfully.")
        else:
            logger.warn(f"Token [id={token_id}] was already locked or does not exist.")

    async def unlock(self, token_id: int) -> None:
        success = await self._repository.unlock_token(token_id)
        if success:
            logger.info(f"Token [id={token_id}] unlocked successfully.")
        else:
            logger.warn(f"Token [id={token_id}] was already unlocked or does not exist.")

    async def delete(self, token_id: int) -> None:
        await self._repository.delete_token_by_id(token_id)


token_service = TokenService(token_repository, token_encryptor)
