"""Main FastAPI application for Lesson Shorts Generator."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shorts_generator.core.config import settings
from shorts_generator.database.connection import _create_engine
from shorts_generator.database.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting Lesson Shorts Generator v0.1.0")
    print(f"📝 Gemini Model: {settings.gemini_model}")
    print(f"🔊 TTS Voice: {settings.edge_tts_voice}")
    print(f"💰 Max cost per video: ${settings.max_cost_per_video:.4f}")

    # Create database tables automatically using async engine
    print("📊 Creating database tables...")
    try:
        # Use the existing async engine for table creation
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

    # Start the automation scheduler
    print("⏰ Starting automation scheduler...")
    try:
        from shorts_generator.services.automation_service import start_scheduler
        await start_scheduler()
        print("✅ Automation scheduler ready")
    except Exception as e:
        import traceback
        print(f"⚠️  Warning: Could not start scheduler: {e}")
        traceback.print_exc()

    yield

    # Shutdown
    print("🛑 Shutting down Lesson Shorts Generator")
    try:
        from shorts_generator.services.automation_service import stop_scheduler
        await stop_scheduler()
    except Exception:
        pass


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
from shorts_generator.routes import (  # noqa: E402
    analytics,
    automation,
    batch,
    cost_monitor,
    daily_automation,
    engagement,
    generate,
    recommendations,
    shorts,
    status,
)

app.include_router(generate.router)
app.include_router(batch.router)
app.include_router(status.router)
app.include_router(engagement.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(cost_monitor.router)
app.include_router(automation.router)
app.include_router(daily_automation.router)  # New daily automation API
app.include_router(shorts.router)


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
