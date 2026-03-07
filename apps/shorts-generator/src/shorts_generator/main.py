"""Main FastAPI application for Lesson Shorts Generator."""

import asyncio
import logging
import signal
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shorts_generator.core.config import settings
from shorts_generator.database.connection import _create_engine
from shorts_generator.database.models import Base

# Configure detailed logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events with proper cleanup.
    """
    # Track background tasks for cleanup
    background_tasks: set[asyncio.Task] = set()

    # Startup
    print("🚀 Starting Lesson Shorts Generator v0.1.0")
    print(f"📝 Gemini Model: {settings.gemini_model}")
    print(f"🔊 TTS Voice: {settings.edge_tts_voice}")
    print(f"💰 Max cost per video: ${settings.max_cost_per_video:.4f}")

    # Create database tables automatically using async engine
    print("📊 Creating database tables...")
    try:
        async_engine = _create_engine()
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await async_engine.dispose()
        print("✅ Database tables ready")
    except Exception as e:
        import traceback
        print(f"⚠️  Warning: Could not create tables: {e}")
        print("   Tables may already exist or database needs configuration")
        traceback.print_exc()



    print("🎯 Startup complete, server ready to accept requests")

    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"🛑 Received signal {sig}, initiating graceful shutdown...")
        # This will trigger the lifespan shutdown
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    yield

    # Shutdown - cancel all background tasks
    print("\n🛑 Shutting down Lesson Shorts Generator")

    # Cancel background tasks
    if background_tasks:
        logger.info(f"Cancelling {len(background_tasks)} background tasks...")
        for task in background_tasks:
            if not task.done():
                task.cancel()
        # Wait for tasks to be cancelled
        await asyncio.gather(*background_tasks, return_exceptions=True)
        logger.info("✅ All background tasks cancelled")



    print("👋 Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Lesson Shorts Generator",
    description="Automated short video generation from lesson content",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check is handled by status.router at /api/v1/health
# Import and include routes
from shorts_generator.routes import shorts, status, daily_automation  # noqa: E402

app.include_router(shorts.router)
app.include_router(status.router)
app.include_router(daily_automation.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Lesson Shorts Generator API",
        "version": "0.1.0",
        "description": "Automated short video generation from lesson content",
        "endpoints": {
            "health": "/api/v1/health",
            "shorts_health": "/api/v1/shorts/health",
            "generate_short": "POST /api/v1/shorts/generate/from-markdown",
            "job_status": "GET /api/v1/shorts/jobs/{job_id}",
            "list_videos": "GET /api/v1/shorts/videos",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
