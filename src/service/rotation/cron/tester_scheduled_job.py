import random
from typing import List, Dict, Any

from src.repository.event_repository import event_repository
from src.service.ai.impl.open_router_processor_service import open_router_processor_service
from src.util.logger import get_logger

logger = get_logger(__name__)


open_router_free_models: set = {
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-4-scout:free",
    "qwen/qwen3-4b:free",
    "microsoft/mai-ds-r1:free",
    "deepseek/deepseek-r1-0528-qwen3-8b:free" }


def get_random_model():
    return random.choice(list(open_router_free_models))


async def tester_scheduled_job():
    logger.info("Running scheduled job for the 'Rotation Service' testing...")

    raw_events: List[Dict[str, Any]] = await event_repository.search_raw_event_with_limit(limit=3)

    for raw_event in raw_events:
        try:
            await open_router_processor_service.process(get_random_model(), raw_event.get('raw_text'))
        except Exception as e:
            logger.warning(f"Failed to process raw_event, exception: '{e}'")

    logger.info("Ending scheduled job for the 'Rotation Service' testing...")
