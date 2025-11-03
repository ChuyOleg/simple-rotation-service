from src.config.settings import settings
from src.model.api_provider import ApiProvider
from src.repository.ai_api_error_repository import AiApiErrorsRepository, ai_api_errors_repository
from src.service.ai.ai_processor_service import AiProcessorService
from src.service.rotation.rate_checking.impl.open_router_rate_limit_checker import open_router_rate_limit_checker
from src.service.rotation.rate_checking.rate_limit_checker import RateLimitChecker
from src.service.rotation.token_service import TokenService, token_service
from src.util.logger import get_logger

logger = get_logger(__name__)


class OpenRouterProcessorService(AiProcessorService):
    _API_PROVIDER: ApiProvider = ApiProvider.OPEN_ROUTER
    _BASE_URL: str = "https://openrouter.ai/api/v1"

    def __init__(self, http_call_retry_count: int, rotation_retry_count: int,
                 ai_api_errors_repo: AiApiErrorsRepository, token_management_service: TokenService,
                 rate_limit_checker: RateLimitChecker):
        super().__init__(self._API_PROVIDER, self._BASE_URL,
                         http_call_retry_count, rotation_retry_count,
                         ai_api_errors_repo, token_management_service, rate_limit_checker)


# model='deepseek/deepseek-r1:free' - the most
# model='meta-llama/llama-4-scout:free'
# model='microsoft/mai-ds-r1:free'
# model='qwen/qwen3-4b:free'
# model='deepseek/deepseek-r1-0528-qwen3-8b:free'
open_router_processor_service: AiProcessorService = OpenRouterProcessorService(
    http_call_retry_count=settings.open_router_settings.http_call_retry_count,
    rotation_retry_count=settings.open_router_settings.rotation_retry_count,
    ai_api_errors_repo=ai_api_errors_repository,
    token_management_service=token_service,
    rate_limit_checker=open_router_rate_limit_checker)
