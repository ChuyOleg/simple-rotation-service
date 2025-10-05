from fastapi import APIRouter
from pydantic import BaseModel

from src.model.api_provider import ApiProvider
from src.service.ai.ai_processor_service import AiProcessorService
from src.service.ai.impl.open_ai_processor_service import open_ai_processor_service
from src.service.ai.impl.open_router_processor_service import open_router_processor_service

router = APIRouter()


class RequestBody(BaseModel):
    api_provider: ApiProvider
    raw_event: str


ai_processors_map: dict[ApiProvider, AiProcessorService] = {
    ApiProvider.OPEN_AI: open_ai_processor_service,
    ApiProvider.OPEN_ROUTER: open_router_processor_service
}


@router.post("/ai/processing")
async def process_event_by_deepseek_r1(body: RequestBody):
    service: AiProcessorService = ai_processors_map.get(body.api_provider)
    return await service.process(body.raw_event)
