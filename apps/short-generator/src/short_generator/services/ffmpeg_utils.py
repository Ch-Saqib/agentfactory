"""FFmpeg binary resolution utility.

Resolves ffmpeg/ffprobe binary paths with fallback:
1. System PATH (e.g., apt-get install ffmpeg)
2. static-ffmpeg Python package (works on managed platforms like FastAPI Cloud)
"""

import shutil
import logging

logger = logging.getLogger(__name__)

_ffmpeg_path: str | None = None
_ffprobe_path: str | None = None


def get_ffmpeg_path() -> str:
    """Return the absolute path to the ffmpeg binary."""
    global _ffmpeg_path
    if _ffmpeg_path is None:
        _ffmpeg_path = _resolve("ffmpeg")
    return _ffmpeg_path


def get_ffprobe_path() -> str:
    """Return the absolute path to the ffprobe binary."""
    global _ffprobe_path
    if _ffprobe_path is None:
        _ffprobe_path = _resolve("ffprobe")
    return _ffprobe_path


def _resolve(name: str) -> str:
    """Resolve a binary name to an absolute path.

    Tries system PATH first, then falls back to static-ffmpeg.
    """
    # 1. Check system PATH
    path = shutil.which(name)
    if path:
        logger.info(f"Found {name} in system PATH: {path}")
        return path

    # 2. Fall back to static-ffmpeg package
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        path = shutil.which(name)
        if path:
            logger.info(f"Found {name} via static-ffmpeg: {path}")
            return path
    except ImportError:
        logger.debug("static-ffmpeg package not installed")
    except Exception as e:
        logger.warning(f"static-ffmpeg failed to provide {name}: {e}")

    # If nothing found, return the bare name and let subprocess handle the error
    logger.warning(f"Could not resolve {name}, using bare command name")
    return name
