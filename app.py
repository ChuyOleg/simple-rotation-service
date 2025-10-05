from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from src.config.settings import settings
from src.database.migration.migration_manager import migration_manager
from src.database.pool.connection_pool_manager import connection_pool_manager
from src.exception.exception_handler import InternalException, RetryableException, internal_exception_handler, \
    retryable_exception_handler
from src.router import token_router, ai_router
from src.service.ai.impl.open_ai_processor_service import open_ai_processor_service
from src.service.ai.impl.open_router_processor_service import open_router_processor_service
from src.service.rotation.cron.token_scheduled_job import unlock_tokens_scheduled_job
from src.util.logger import setup_logging, log_startup_info, get_logger

setup_logging()
log_startup_info()

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connection_pool_manager.connect()
    logger.info("DBs pool created")

    await migration_manager.run_migrations()
    logger.info("DB migration has been performed for local Postgres.")

    await open_ai_processor_service.init_ai_client()
    await open_router_processor_service.init_ai_client()
    logger.info("AI clients have been initialized.")

    scheduler.add_job(unlock_tokens_scheduled_job, CronTrigger.from_crontab(settings.rotation.cron))
    scheduler.start()

    yield

    await connection_pool_manager.disconnect()
    logger.info("✅ DBs pool disconnected")

    scheduler.shutdown()


app = FastAPI(title="Local OpenAI API Proxy", lifespan=lifespan)

app.add_exception_handler(InternalException, internal_exception_handler)
app.add_exception_handler(RetryableException, retryable_exception_handler)

app.include_router(ai_router.router, tags=["AI"])
app.include_router(token_router.router, tags=["Token"])
