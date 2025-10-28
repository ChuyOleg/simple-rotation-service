from typing import Any, Dict, List

from ..database.pool.connection_pool_manager import ConnectionPoolManager, connection_pool_manager_instance
from ..util.logger import get_logger

logger = get_logger(__name__)


class EventRepository:
    def __init__(self, connection_pool_manager: ConnectionPoolManager) -> None:
        self._connection_pool_manager = connection_pool_manager

    async def search_raw_event_with_limit(self, limit: int = 100) -> List[Dict[str, Any]]:
        async with self._connection_pool_manager.acquire_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM processed_events
                ORDER BY created_at DESC 
                LIMIT $1
            """, limit)

            return [{
                'id': row['id'],
                'post_created_at': row['post_created_at'],
                'post_scraped_at': row['post_scraped_at'],
                'raw_text': row['raw_text'], }
                for row in rows]


event_repository = EventRepository(connection_pool_manager_instance)
