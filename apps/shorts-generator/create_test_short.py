"""Create a test short video in the database for UI testing."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from shorts_generator.core.config import settings
from shorts_generator.models import ShortVideo, Base
from uuid import uuid4


async def create_test_short():
    """Create a test short video in the database."""

    # Create async engine
    database_url = settings.shorts_database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    # Remove sslmode from URL
    database_url = database_url.split("?")[0].split("&")[0]

    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"ssl": True, "server_settings": {"jit": "off"}},
    )

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create test short
        test_short = ShortVideo(
            id=str(uuid4()),
            lesson_path="01-General-Agents-Foundations/01-agent-factory-paradigm",
            title="What is AI Agency? 🤖",
            script="""AI agents are autonomous systems that can pursue goals without constant human guidance.

Unlike traditional automation that follows rigid rules, AI agents can:
• Reason through complex problems
• Plan multi-step actions
• Adapt to changing circumstances
• Learn from experience

Think of an agent as a digital employee that can independently complete tasks like research, coding, or customer service.

The Agent Factory paradigm takes this further - creating domain experts that can teach, build, and collaborate alongside humans.

Ready to build your first AI agent? Let's dive in!""",
            duration_seconds=60,
            video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            thumbnail_url="https://picsum.photos/400/700?random=1",
            captions_url="",
            generation_cost=0.005,
        )

        session.add(test_short)
        await session.commit()
        await session.refresh(test_short)

        print(f"✅ Test short created!")
        print(f"   ID: {test_short.id}")
        print(f"   Title: {test_short.title}")
        print(f"   Duration: {test_short.duration_seconds}s")
        print(f"   Video URL: {test_short.video_url}")
        print(f"\n📺 View at: http://localhost:3000/shorts")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_test_short())
