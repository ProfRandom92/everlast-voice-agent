# LangGraph Checkpointer for Everlast Voice Agent
# Supports SQLite (dev) and PostgreSQL/Supabase (production)
# Thread-ID = Caller Phone Number for session persistence

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import sqlite3
from contextlib import contextmanager
import os

# Try to import asyncpg for PostgreSQL support
try:
    import asyncpg
    from asyncpg import Pool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Try to import aiosqlite for async SQLite
try:
    import aiosqlite
    ASYNC_SQLITE_AVAILABLE = True
except ImportError:
    ASYNC_SQLITE_AVAILABLE = False


class BaseCheckpointer:
    """Base class for checkpointers"""

    async def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint for a thread"""
        raise NotImplementedError

    async def set(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save checkpoint for a thread"""
        raise NotImplementedError

    async def delete(self, thread_id: str) -> None:
        """Delete checkpoint for a thread"""
        raise NotImplementedError

    async def list_threads(self, limit: int = 100) -> List[str]:
        """List all thread IDs"""
        raise NotImplementedError


class SqliteSaver(BaseCheckpointer):
    """
    SQLite-based checkpointer for development.
    Thread-ID = Phone number for call session persistence.
    """

    def __init__(self, db_path: str = "checkpoints.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_updated_at ON checkpoints(updated_at)
            """)
            conn.commit()

    async def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint by thread ID (phone number)"""
        if ASYNC_SQLITE_AVAILABLE:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute(
                    "SELECT state FROM checkpoints WHERE thread_id = ?",
                    (thread_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
                    return None
        else:
            # Fallback to sync
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT state FROM checkpoints WHERE thread_id = ?",
                    (thread_id,)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None

    async def set(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save checkpoint - thread_id is the caller's phone number"""
        state_json = json.dumps(state, default=str)

        if ASYNC_SQLITE_AVAILABLE:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT INTO checkpoints (thread_id, state, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(thread_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = CURRENT_TIMESTAMP
                """, (thread_id, state_json))
                await conn.commit()
        else:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO checkpoints (thread_id, state, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(thread_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = CURRENT_TIMESTAMP
                """, (thread_id, state_json))
                conn.commit()

    async def delete(self, thread_id: str) -> None:
        """Delete checkpoint"""
        if ASYNC_SQLITE_AVAILABLE:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    "DELETE FROM checkpoints WHERE thread_id = ?",
                    (thread_id,)
                )
                await conn.commit()
        else:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM checkpoints WHERE thread_id = ?",
                    (thread_id,)
                )
                conn.commit()

    async def list_threads(self, limit: int = 100) -> List[str]:
        """List all thread IDs (phone numbers)"""
        if ASYNC_SQLITE_AVAILABLE:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute(
                    "SELECT thread_id FROM checkpoints ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT thread_id FROM checkpoints ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
                return [row[0] for row in cursor.fetchall()]


class PostgresSaver(BaseCheckpointer):
    """
    PostgreSQL/Supabase-based checkpointer for production.
    Thread-ID = Phone number for call session persistence.
    """

    def __init__(self, dsn: Optional[str] = None):
        if not POSTGRES_AVAILABLE:
            raise ImportError("asyncpg is required for PostgreSQL support. Install with: pip install asyncpg")

        self.dsn = dsn or os.getenv("DATABASE_URL", "postgresql://localhost/everlast")
        self.pool: Optional[Pool] = None

    async def connect(self):
        """Initialize connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.dsn, min_size=5, max_size=20)
            await self._init_db()

    async def _init_db(self):
        """Initialize database schema"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT PRIMARY KEY,
                    state JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoints_updated_at
                ON checkpoints(updated_at DESC)
            """)

    async def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint by thread ID (phone number)"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT state FROM checkpoints WHERE thread_id = $1",
                thread_id
            )
            if row:
                return dict(row['state'])
            return None

    async def set(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save checkpoint - thread_id is the caller's phone number"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO checkpoints (thread_id, state, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (thread_id) DO UPDATE SET
                    state = EXCLUDED.state,
                    updated_at = NOW()
            """, thread_id, json.dumps(state, default=str))

    async def delete(self, thread_id: str) -> None:
        """Delete checkpoint"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = $1",
                thread_id
            )

    async def list_threads(self, limit: int = 100) -> List[str]:
        """List all thread IDs (phone numbers)"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT thread_id FROM checkpoints ORDER BY updated_at DESC LIMIT $1",
                limit
            )
            return [row['thread_id'] for row in rows]

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None


class SupabaseSaver(BaseCheckpointer):
    """
    Supabase-compatible checkpointer using Supabase client.
    Stores checkpoints in the 'checkpoints' table.
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(
                supabase_url or os.getenv("SUPABASE_URL"),
                supabase_key or os.getenv("SUPABASE_SERVICE_KEY")
            )
        except ImportError:
            raise ImportError("supabase-py is required. Install with: pip install supabase")

    async def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint by thread ID (phone number)"""
        result = self.supabase.table("checkpoints").select("state").eq("thread_id", thread_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]['state']
        return None

    async def set(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save checkpoint - thread_id is the caller's phone number"""
        # Check if exists
        existing = await self.get(thread_id)

        if existing:
            # Update
            self.supabase.table("checkpoints").update({
                "state": state,
                "updated_at": datetime.now().isoformat()
            }).eq("thread_id", thread_id).execute()
        else:
            # Insert
            self.supabase.table("checkpoints").insert({
                "thread_id": thread_id,
                "state": state,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()

    async def delete(self, thread_id: str) -> None:
        """Delete checkpoint"""
        self.supabase.table("checkpoints").delete().eq("thread_id", thread_id).execute()

    async def list_threads(self, limit: int = 100) -> List[str]:
        """List all thread IDs (phone numbers)"""
        result = self.supabase.table("checkpoints").select("thread_id").order("updated_at", desc=True).limit(limit).execute()
        return [row['thread_id'] for row in result.data] if result.data else []


# Factory function
def get_checkpointer(
    backend: str = "sqlite",
    **kwargs
) -> BaseCheckpointer:
    """
    Get appropriate checkpointer based on backend.

    Args:
        backend: "sqlite", "postgres", or "supabase"
        **kwargs: Backend-specific arguments

    Returns:
        Configured checkpointer instance
    """
    if backend == "sqlite":
        return SqliteSaver(**kwargs)
    elif backend == "postgres":
        return PostgresSaver(**kwargs)
    elif backend == "supabase":
        return SupabaseSaver(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_checkpointer():
        # Use SQLite for testing
        checkpointer = SqliteSaver("test_checkpoints.db")

        # Simulate a call session
        phone_number = "+49123456789"

        # Save state
        test_state = {
            "conversation_id": "conv-123",
            "phone_number": phone_number,
            "bant": {
                "budget": "Ja",
                "authority": "Entscheider",
                "need": "Hoch",
                "timeline": "1-3 Monate"
            },
            "lead_score": "A",
            "messages": ["Guten Tag", "Ja, ich bin interessiert"]
        }

        await checkpointer.set(phone_number, test_state)
        print(f"Saved checkpoint for {phone_number}")

        # Retrieve state (simulating return caller)
        retrieved = await checkpointer.get(phone_number)
        print(f"Retrieved state: {retrieved}")

        # List all active threads
        threads = await checkpointer.list_threads()
        print(f"Active threads: {threads}")

        # Cleanup
        await checkpointer.delete(phone_number)
        print("Checkpoint deleted")

    asyncio.run(test_checkpointer())
