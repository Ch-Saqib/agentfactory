"""Compatibility module for legacy ``src.short_generator.main`` imports."""

try:
    from ..shorts_generator.main import app
except ImportError:
    from shorts_generator.main import app

__all__ = ["app"]
