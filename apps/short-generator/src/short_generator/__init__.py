"""Compatibility package for legacy ``short_generator`` imports."""

try:
    from ..shorts_generator import __version__
except ImportError:
    from shorts_generator import __version__

__all__ = ["__version__"]
