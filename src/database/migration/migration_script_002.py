import asyncpg


async def migration_002_create_ai_api_errors_table(conn: asyncpg.Connection) -> None:

    """Create the ai_tokens table."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_api_errors (
            id SERIAL PRIMARY KEY,
            error_text TEXT NOT NULL,
            ai_model TEXT NOT NULL
        )
    """)
