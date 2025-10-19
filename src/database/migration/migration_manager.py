"""Database migration manager for handling schema changes."""

from typing import List, Callable, Awaitable
import asyncpg

from src.config.settings import settings
from src.database.migration.migration_script_001 import migration_001_create_ai_tokens_table
from src.util.logger import get_logger

logger = get_logger(__name__)


class Migration:
    """Represents a database migration."""
    
    def __init__(self, version: int, name: str, up_func: Callable[[asyncpg.Connection], Awaitable[None]]):
        self.version = version
        self.name = name
        self.up_func = up_func
    
    async def up(self, conn: asyncpg.Connection) -> None:
        """Execute the migration."""
        await self.up_func(conn)


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, postgres_connection_string: str) -> None:
        self.connection_string = postgres_connection_string
        self.migrations: List[Migration] = []
        self._register_migrations()
    
    def _register_migrations(self) -> None:
        """Register all migrations."""
        self.migrations = [
            Migration(1, "create_ai_tokens_table", migration_001_create_ai_tokens_table),
        ]
        # Sort by version
        self.migrations.sort(key=lambda m: m.version)
    
    async def create_migrations_table(self, conn: asyncpg.Connection) -> None:
        """Create the migrations tracking table."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations_for_rotation (
                id SERIAL PRIMARY KEY,
                version INTEGER UNIQUE NOT NULL,
                migration_name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
    
    async def get_applied_migrations(self, conn: asyncpg.Connection) -> List[int]:
        """Get list of already applied migration versions."""
        rows = await conn.fetch("""
            SELECT version FROM migrations_for_rotation 
            ORDER BY version
        """)
        return [row['version'] for row in rows]
    
    async def mark_migration_applied(
        self, 
        conn: asyncpg.Connection, 
        version: int,
        migration_name: str
    ) -> None:
        """Mark a migration as applied."""
        await conn.execute("""
            INSERT INTO migrations_for_rotation (version, migration_name)
            VALUES ($1, $2)
        """, version, migration_name)
    
    async def run_migration(self, conn: asyncpg.Connection, migration: Migration) -> None:
        """Run a single migration."""
        logger.info(f"Running migration: {migration.name} (version {migration.version})")
        
        try:
            # Execute the migration
            await migration.up(conn)
            
            # Mark as applied
            await self.mark_migration_applied(conn, migration.version, migration.name)
            
            logger.info(f"Migration applied successfully: {migration.name}")
            
        except Exception as e:
            logger.error(f"Migration failed: {migration.name}", error=str(e))
            raise
    
    async def run_migrations(self) -> None:
        """Run all pending migrations."""
        logger.info("Starting database migrations")
        
        try:
            # Connect to database
            conn = await asyncpg.connect(self.connection_string)
            
            try:
                # Create migrations table if it doesn't exist
                await self.create_migrations_table(conn)
                
                # Get applied migrations
                applied_versions = await self.get_applied_migrations(conn)
                
                # Find pending migrations
                pending_migrations = [
                    migration for migration in self.migrations
                    if migration.version not in applied_versions
                ]
                
                if not pending_migrations:
                    logger.info("No pending migrations")
                    return
                
                logger.info(f"Found {len(pending_migrations)} pending migrations")
                
                # Run pending migrations
                for migration in pending_migrations:
                    await self.run_migration(conn, migration)
                
                logger.info("All migrations completed successfully")
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error("Migration process failed", error=str(e))
            raise

migration_manager = MigrationManager(settings.postgres.connection_string)
