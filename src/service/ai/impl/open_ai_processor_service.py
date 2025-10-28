from typing import override

from src.model.api_provider import ApiProvider
from src.repository.ai_api_error_repository import AiApiErrorsRepository, ai_api_errors_repository
from src.service.ai.ai_processor_service import AiProcessorService
from src.service.rotation.token_service import TokenService, token_service
from src.util.logger import get_logger

logger = get_logger(__name__)


class OpenAIProcessorService(AiProcessorService):
    _API_PROVIDER: ApiProvider = ApiProvider.OPEN_AI
    _BASE_URL: str = "https://api.openai.com/v1"

    def __init__(self, ai_api_errors_repo: AiApiErrorsRepository, token_management_service: TokenService):
        super().__init__(self._API_PROVIDER, self._BASE_URL, ai_api_errors_repo, token_management_service)

    @override
    def _is_rate_limit_exception(self, e: Exception) -> bool:
        # ToDo: 01/10 Mocked now, add real implementation
        return True


open_ai_processor_service: AiProcessorService = OpenAIProcessorService(
    ai_api_errors_repo=ai_api_errors_repository,
    token_management_service=token_service)
