from src.config.settings import settings
from src.model.api_provider import ApiProvider
from src.repository.ai_api_error_repository import AiApiErrorsRepository, ai_api_errors_repository
from src.service.ai.ai_processor_service import AiProcessorService
from src.service.rotation.rate_checking.impl.open_ai_rate_limit_checker import open_ai_rate_limit_checker
from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker
from src.service.rotation.token_service import TokenService, token_service
from src.util.logger import get_logger

logger = get_logger(__name__)


class OpenAIProcessorService(AiProcessorService):
    _API_PROVIDER: ApiProvider = ApiProvider.OPEN_AI
    _BASE_URL: str = "https://api.openai.com/v1"

    def __init__(self, http_call_retry_count: int, rotation_retry_count: int,
                 ai_api_errors_repo: AiApiErrorsRepository, token_management_service: TokenService,
                 rate_limit_checker: RateLimitChecker):
        super().__init__(self._API_PROVIDER, self._BASE_URL,
                         http_call_retry_count, rotation_retry_count,
                         ai_api_errors_repo, token_management_service, rate_limit_checker)


open_ai_processor_service: AiProcessorService = OpenAIProcessorService(
    http_call_retry_count=settings.open_ai_settings.http_call_retry_count,
    rotation_retry_count=settings.open_ai_settings.rotation_retry_count,
    ai_api_errors_repo=ai_api_errors_repository,
    token_management_service=token_service,
    rate_limit_checker=open_ai_rate_limit_checker)
