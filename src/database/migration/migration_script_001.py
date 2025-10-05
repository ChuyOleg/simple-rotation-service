import asyncpg


async def migration_001_create_ai_tokens_table(conn: asyncpg.Connection) -> None:

    """Create the ai_tokens table."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id SERIAL PRIMARY KEY,
            token_encrypted TEXT NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            api_provider TEXT NOT NULL,
            locked_at TIMESTAMP WITH TIME ZONE
        )
    """)
