from abc import ABC, abstractmethod

from src.model.event import create_system_message_prompt, create_user_message_prompt
from src.model.ukrainian_event import UkrainianEvent
from src.service.rotation.rotatable_service import RotatableService
from src.service.rotation.token_service import TokenService
from src.util.logger import get_logger

logger = get_logger(__name__)


class AiProcessorService(RotatableService, ABC):

    def __init__(self, api_model: str, token_service: TokenService):
        self._api_model = api_model
        self._token_service = token_service

    async def process(self, raw_event: str) -> UkrainianEvent | None:
        system_part: dict[str, str] = create_system_message_prompt()
        user_part: dict[str, str] = create_user_message_prompt(raw_event)

        processed_event = await self._process_with_retry(system_part, user_part)
        return processed_event

    @abstractmethod
    async def init_ai_client(self):
        pass
