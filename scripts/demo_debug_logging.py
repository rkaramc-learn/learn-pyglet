#!/usr/bin/env python3
"""Demo script to show debug logging output.

Runs the game initialization with DEBUG logging enabled to show all log output.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyglet_readme.logging_config import init_logging, get_logger
from pyglet_readme.assets import get_loader

# Setup DEBUG logging
init_logging(level=logging.DEBUG)

logger = get_logger(__name__)

logger.info("=" * 70)
logger.info("DEMO: Running Game Initialization with DEBUG Logging Enabled")
logger.info("=" * 70)

logger.info("Initializing asset loader...")
loader = get_loader()

logger.info("Verifying required assets...")
required_assets = {
    "assets/images/kitten.png": "image",
    "assets/sprites/mouse_sheet.png": "image",
    "assets/audio/sfx/meow.wav": "sound",
    "assets/audio/music/ambience.wav": "sound",
}
result = loader.verify_assets(required_assets)

logger.info("Loading game assets...")
try:
    kitten = loader.load_image("assets/images/kitten.png")
    logger.info(f"Kitten sprite loaded: {kitten.width}x{kitten.height}")
except Exception as e:
    logger.error(f"Failed to load kitten: {e}")

logger.info("Attempting mouse sprite...")
try:
    mouse = loader.load_image("assets/sprites/mouse_sheet.png")
    logger.info(f"Mouse sprite sheet loaded: {mouse.width}x{mouse.height}")
except FileNotFoundError:
    logger.warning("Mouse sprite sheet not found (expected)")

logger.info("Attempting sound effects...")
try:
    meow = loader.load_sound("assets/audio/sfx/meow.wav", streaming=False)
    logger.info("Meow sound loaded successfully")
except FileNotFoundError:
    logger.warning("Meow sound not found")

logger.info("Attempting background music...")
try:
    ambience = loader.load_sound("assets/audio/music/ambience.wav")
    logger.info("Ambience music loaded successfully")
except FileNotFoundError:
    logger.warning("Ambience music not found (expected)")

logger.info("=" * 70)
logger.info("Demo complete - Game initialization successful with DEBUG logging")
logger.info("=" * 70)
