from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine(database_url: str, debug: bool = False) -> AsyncEngine:
    """ساخت engine برای SQLite."""
    return create_async_engine(
        database_url,
        echo=debug,
        future=True,
        connect_args={"check_same_thread": False},
    )