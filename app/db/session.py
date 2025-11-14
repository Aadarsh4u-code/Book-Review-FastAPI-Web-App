from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings, EnvironmentSchema
from app.db.base import Base

# Create the async engine
async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == EnvironmentSchema.DEV, # Log SQL queries (optional)
    future=True,
    pool_size=20, # Keep 20 persistent connections ready
    max_overflow=10 # Allow up to 10 extra temporary connections if pool is full. Now total=30 pool connection
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    # async with AsyncSessionLocal() as session:
    #     yield session
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # auto commit if no exception
        except Exception:
            await session.rollback()  # auto rollback on error
            raise
        finally:
            await session.close()  # always close session

# DB initializer |  Only for development - use Alembic in production
async def init_db():
    async with async_engine.begin() as conn:
        # Import models so they are registered in Base.metadata
        # (SQLAlchemy discovers them by executing the class definitions)
        from app.books.models import BookModel
        from app.user.models import UserModel
        from app.reviews.models import ReviewModel
        await conn.run_sync(Base.metadata.create_all)