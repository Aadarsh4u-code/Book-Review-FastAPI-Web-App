from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import setting
from app.db.base import Base

# Create the async engine
async_engine = create_async_engine(
    url=setting.DATABASE_URL,
    echo=True,  # Log SQL queries (optional)
    pool_size=20, # Keep 20 persistent connections ready
    max_overflow=10 # Allow up to 10 extra temporary connections if pool is full. Now total=30 pool connection
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# DB initializer |  Only for development - use Alembic in production
async def init_db():
    async with async_engine.begin() as conn:
        # Import models so they are registered in Base.metadata
        # (SQLAlchemy discovers them by executing the class definitions)
        from app.books.models import BookModel
        from app.user.models import UserModel
        await conn.run_sync(Base.metadata.create_all)