from typing import Optional

import asyncpg
from asyncpg import Pool

from src.config.settings import settings
from src.util.logger import get_logger


logger = get_logger(__name__)

class ConnectionPoolManager:

    def __init__(self, postgres_connection_string: str):
        self._pool: Optional[Pool] = None
        self._connection_string = postgres_connection_string

    async def connect(self) -> None:
        """Establish connection pool to PostgreSQL."""
        try:
            self._pool = await asyncpg.create_pool(
                self._connection_string,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': f"uopp-data-processor-events"
                }
            )
            logger.info("Postgres connection pool established")
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL.", error=str(e))
            raise

    def acquire_connection(self):
        return self._pool.acquire()

    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Postgres connection pool closed")


connection_pool_manager_instance = ConnectionPoolManager(settings.postgres.connection_string)
