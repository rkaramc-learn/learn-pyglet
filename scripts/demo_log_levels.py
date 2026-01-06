#!/usr/bin/env python3
"""Demo showing different logging levels.

Compares INFO vs DEBUG logging output.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyglet_readme.logging_config import init_logging, close_logging, get_logger
from pyglet_readme.assets import get_loader


def run_demo(level: int, level_name: str) -> None:
    """Run demo with specified logging level.

    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        level_name: Display name for the level
    """
    print()
    print("=" * 70)
    print(f"Logging Level: {level_name}")
    print("=" * 70)
    print()

    # Initialize logging
    init_logging(level=level)
    logger = get_logger(__name__)

    # Simulate game initialization
    logger.info("Initializing asset loader")
    loader = get_loader()

    logger.info("Verifying assets")
    required_assets = {
        "assets/images/kitten.png": "image",
        "assets/sprites/mouse_sheet.png": "image",
    }
    loader.verify_assets(required_assets)

    logger.info("Loading kitten sprite")
    kitten = loader.load_image("assets/images/kitten.png")

    # Cleanup
    close_logging()


if __name__ == "__main__":
    # Suppress newlines between runs
    run_demo(logging.INFO, "INFO (default)")
    run_demo(logging.DEBUG, "DEBUG (verbose mode)")

    print()
    print("=" * 70)
    print("Notice: DEBUG level shows detailed asset paths and load times")
    print("=" * 70)
