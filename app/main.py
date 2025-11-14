from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.auth.routes import auth_router
from app.books.routes import book_router
from app.core.config import settings, EnvironmentSchema
from app.core.logger import logger
from app.core.middleware import register_middleware
from app.db.redis import redis_client
from app.db.session import init_db
from app.reviews.routes import reviews_router
from app.shared.exception_handlers import register_exception_handlers

version = "v1"
description = """
A REST API for a book review web service.
This REST API is able to;
    - Create Read Update And delete books
    - Add reviews to books
    - Add tags to Books e.t.c.
"""



version_prefix =f"/api/{version}"

@asynccontextmanager
async def lifespan(apps: FastAPI):
    # Startup
    print(f" 🛜 Server is starting... 🛜. ")

    # Initialize Redis
    await redis_client.init_redis()
    print("✅ Redis initialized successfully")

    # Only auto-create tables in development
    if settings.ENVIRONMENT == EnvironmentSchema.DEV:
        print(f"📝 Running in {EnvironmentSchema.DEV} mode - auto-creating tables")
        await init_db()
    else:
        print("🚀 Running in {EnvironmentSchema.DEV} mode - use Alembic migrations")

    yield # App runs here

    # Shutdown
    await redis_client.close_redis()
    print(f" 🛑 Server has been stopped 🛑 and Redis closed. ")

def create_app() -> FastAPI:
    fastapi_app = FastAPI(
        title=settings.APP_NAME,
        description=description,
        version=version,
        license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
        lifespan=lifespan,
        contact={
            "name": "Aadarsh Kushwaha",
            "url": "https://github.com/Aadarsh4u-code",
            "email": "aadarshkushwaha0208@gmail.com",
        },
        terms_of_service="https://example.com/book_review_api",
        openapi_url=f"{version_prefix}/openapi.json",
        docs_url=f"{version_prefix}/docs",
        redoc_url=f"{version_prefix}/redoc"
    )

    # Register custom Middleware
    register_middleware(fastapi_app)

    # Register custom exception handlers
    register_exception_handlers(fastapi_app)


    # Include routers
    fastapi_app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["v1 | 👮🏻‍♀️ Authentication"])
    fastapi_app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["v1 | 📚 Books"])
    fastapi_app.include_router(reviews_router, prefix=f"{version_prefix}/reviews", tags=["v1 | 👁️‍🗨️ Reviews"])

    logger.info("✅ Application initialized ....!!!!")
    return fastapi_app

# Call FastAPI App
app = create_app()
