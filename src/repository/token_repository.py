from typing import Dict, Any, Optional, List

from src.database.pool.connection_pool_manager import connection_pool_manager, ConnectionPoolManager
from src.mapping.api_token_mapper import map_db_row_to_api_token_dict
from src.model.api_provider import ApiProvider


class TokenRepository:

    def __init__(self, connection_pool_manager: ConnectionPoolManager) -> None:
        self._connection_pool_manager = connection_pool_manager

    async def get_by_id(self, token_id: int) -> Optional[Dict[str, Any]]:
        query = """
         SELECT id, api_provider, token_encrypted
         FROM tokens
         WHERE id = $1"""

        async with self._connection_pool_manager.acquire_connection() as conn:
            row = await conn.fetchrow(query, token_id)
            return map_db_row_to_api_token_dict(row) if row else None

    async def get_random_by_api_provider(self, api_provider: ApiProvider) -> Optional[Dict[str, Any]]:
        query = """
         SELECT id, api_provider, token_encrypted
         FROM tokens
         WHERE api_provider = $1 AND locked_at IS NULL
         ORDER BY RANDOM()
         LIMIT 1"""

        async with self._connection_pool_manager.acquire_connection() as conn:
            row = await conn.fetchrow(query, api_provider.value)
            return map_db_row_to_api_token_dict(row) if row else None

    async def get_locked_tokens(self) -> List[Dict[str, Any]]:
        query = """
         SELECT id, api_provider, token_encrypted
         FROM tokens
         WHERE locked_at IS NOT NULL"""

        async with self._connection_pool_manager.acquire_connection() as conn:
            rows = await conn.fetch(query)
            return [map_db_row_to_api_token_dict(row) for row in rows]

    async def save_token(self, token_encrypted: str, token_hash: str, api_provider: ApiProvider) -> Optional[int]:
        query = """
        INSERT INTO tokens (token_encrypted, token_hash, api_provider)
        VALUES ($1, $2, $3)
        ON CONFLICT DO NOTHING
        RETURNING id
        """
        async with self._connection_pool_manager.acquire_connection() as conn:
            row = await conn.fetchrow(query, token_encrypted, token_hash, api_provider.value)
            return row["id"] if row else None

    async def lock_token(self, token_id: int) -> bool:
        query = """
        UPDATE tokens
        SET locked_at = NOW()
        WHERE id = $1 AND locked_at IS NULL
        RETURNING id;
        """
        async with self._connection_pool_manager.acquire_connection() as conn:
            row = await conn.fetchrow(query, token_id)
            return row is not None

    async def unlock_token(self, token_id: int) -> bool:
        query = """
        UPDATE tokens
        SET locked_at = NULL
        WHERE id = $1 AND locked_at IS NOT NULL
        RETURNING id;
        """
        async with self._connection_pool_manager.acquire_connection() as conn:
            row = await conn.fetchrow(query, token_id)
            return row is not None

    async def delete_token_by_id(self, token_id: int) -> None:
        query = "DELETE FROM tokens WHERE id = $1"
        async with self._connection_pool_manager.acquire_connection() as conn:
            await conn.execute(query, token_id)


token_repository = TokenRepository(connection_pool_manager)
