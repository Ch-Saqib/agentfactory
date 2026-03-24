"""Source-tree compatibility for legacy ``src.*`` imports.

When the app is launched from the project root with an import like
``src.short_generator.main``, the codebase still uses absolute imports such as
``shorts_generator.main``. Add this directory to ``sys.path`` so both forms work.
"""

from pathlib import Path
import sys

_SRC_DIR = Path(__file__).resolve().parent
_src_dir_str = str(_SRC_DIR)

if _src_dir_str not in sys.path:
    sys.path.insert(0, _src_dir_str)

