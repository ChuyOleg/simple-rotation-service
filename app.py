from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from src.config.settings import settings
from src.database.migration.migration_manager import migration_manager
from src.database.pool.connection_pool_manager import connection_pool_manager_instance
from src.exception.exception_handler import InternalException, internal_exception_handler, \
    internal_retryable_exception_handler, rotation_retryable_exception_handler, not_found_token_exception_handler, \
    HttpCallRetryableException, RotationRetryableException, NotFoundTokenException
from src.router import token_router, ai_router
from src.service.rotation.cron.tester_scheduled_job import tester_scheduled_job
from src.service.rotation.cron.token_scheduled_job import unlock_tokens_scheduled_job
from src.util.logger import setup_logging, log_startup_info, get_logger

setup_logging()
log_startup_info()

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connection_pool_manager_instance.connect()
    logger.info("DBs pool created")

    await migration_manager.run_migrations()
    logger.info("DB migration has been performed for Postgres.")

    scheduler.add_job(unlock_tokens_scheduled_job, CronTrigger.from_crontab(settings.rotation.cron))
    scheduler.add_job(tester_scheduled_job, CronTrigger.from_crontab(settings.rotation_tester.cron))
    scheduler.start()

    yield

    await connection_pool_manager_instance.disconnect()
    logger.info("✅ DBs pool disconnected")

    scheduler.shutdown()


app = FastAPI(title="Local OpenAI API Proxy", lifespan=lifespan)

app.add_exception_handler(InternalException, internal_exception_handler)
app.add_exception_handler(HttpCallRetryableException, internal_retryable_exception_handler)
app.add_exception_handler(RotationRetryableException, rotation_retryable_exception_handler)
app.add_exception_handler(NotFoundTokenException, not_found_token_exception_handler)

app.include_router(ai_router.router, tags=["AI"])
app.include_router(token_router.router, tags=["Token"])
