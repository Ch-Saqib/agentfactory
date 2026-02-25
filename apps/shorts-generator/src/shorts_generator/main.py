"""Main FastAPI application for Lesson Shorts Generator."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from shorts_generator.core.config import settings
from shorts_generator.database.connection import _create_engine
from shorts_generator.models import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting Lesson Shorts Generator v0.1.0")
    print(f"📝 Gemini Model: {settings.gemini_model}")
    print(f"🔊 TTS Voice: {settings.edge_tts_voice}")
    print(f"💰 Max cost per video: ${settings.max_cost_per_video:.4f}")

    # Create database tables automatically using async engine
    print("📊 Creating database tables...")
    try:
        from shorts_generator.models import Base
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

    yield

    # Shutdown
    print("🛑 Shutting down Lesson Shorts Generator")


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
from shorts_generator.routes import (
    analytics,
    batch,
    cost_monitor,
    engagement,
    generate,
    recommendations,
    status,
)

app.include_router(generate.router)
app.include_router(batch.router)
app.include_router(status.router)
app.include_router(engagement.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(cost_monitor.router)


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
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
