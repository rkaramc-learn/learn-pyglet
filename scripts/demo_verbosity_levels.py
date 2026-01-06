#!/usr/bin/env python3
"""Demo showing all verbosity levels.

Demonstrates:
- Default (WARN)
- -v (INFO)
- -vv (DEBUG)
- -vvv (TRACE)
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyglet_readme.assets import get_loader
from pyglet_readme.logging_config import TRACE_LEVEL, close_logging, get_logger, init_logging


def show_level(level: int, level_name: str) -> None:
    """Show output for a specific verbosity level.

    Args:
        level: Log level
        level_name: Display name
    """
    print()
    print("=" * 70)
    print(f"Verbosity Level: {level_name}")
    print("=" * 70)
    print()

    # Initialize logging
    init_logging(level=level)
    logger = get_logger(__name__)

    # Log at all levels
    logger.warning("This is a WARNING message")
    logger.info("This is an INFO message")
    logger.debug("This is a DEBUG message")
    if level == TRACE_LEVEL:
        logger.log(TRACE_LEVEL, "This is a TRACE message")

    # Load asset to see asset module logging
    logger.warning("Loading asset...")
    try:
        loader = get_loader()
        loader.load_image("assets/images/kitten.png")
    except Exception as e:
        logger.error(f"Failed to load: {e}")

    # Cleanup
    close_logging()


if __name__ == "__main__":
    show_level(logging.WARNING, "Default (WARN) - uv run pyglet-readme")
    show_level(logging.INFO, "-v (INFO) - uv run pyglet-readme -v")
    show_level(logging.DEBUG, "-vv (DEBUG) - uv run pyglet-readme -vv")
    show_level(TRACE_LEVEL, "-vvv (TRACE) - uv run pyglet-readme -vvv")

    print()
    print("=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"WARN  (default): Only warnings and errors")
    print(f"INFO  (-v):      Key events and milestones")
    print(f"DEBUG (-vv):     Detailed information and flow")
    print(f"TRACE (-vvv):    Ultra-detailed system information")
    print("=" * 70)
