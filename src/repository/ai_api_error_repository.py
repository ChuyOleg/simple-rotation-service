from typing import Optional

from src.database.pool.connection_pool_manager import connection_pool_manager_instance, ConnectionPoolManager


class AiApiErrorsRepository:

    def __init__(self, connection_pool_manager: ConnectionPoolManager) -> None:
        self._connection_pool_manager = connection_pool_manager

    async def save_error(self, error_text: str, ai_model: str) -> Optional[int]:
        query = """
        INSERT INTO ai_api_errors (error_text, ai_model)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        RETURNING id
        """
        async with self._connection_pool_manager.acquire_connection() as conn:
            row = await conn.fetchrow(query, error_text, ai_model)
            return row["id"] if row else None


ai_api_errors_repository = AiApiErrorsRepository(connection_pool_manager_instance)
