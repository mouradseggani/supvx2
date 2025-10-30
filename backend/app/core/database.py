from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData, text
from typing import AsyncGenerator
import logging

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# SQLAlchemy async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Base class for all database models
    """
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_database_connection() -> None:
    """
    Test database connection on startup
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def close_database() -> None:
    """
    Close database connection
    """
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")
        raise