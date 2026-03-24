"""Deployment entrypoint for FastAPI Cloud autodiscovery.

Expose the real ASGI app at the project root so commands that inspect `.`
or `main.py` can find `app` without needing an explicit `--app` path.
"""

from src.shorts_generator.main import app


def main() -> None:
    """Compatibility entrypoint for local execution."""
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)


if __name__ == "__main__":
    main()
