import argparse
import logging
import sys
from pathlib import Path

from .hello_world import run_hello_world
from .logging_config import init_logging


def main() -> None:
    """Entry point for the pyglet-readme application."""
    parser = argparse.ArgumentParser(
        description="Interactive 2D game demonstrating pyglet library features"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug-level logging output",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Write logs to file (default: no file logging)",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_file = Path(args.log_file) if args.log_file else None
    init_logging(level=log_level, log_file=log_file)

    logger = logging.getLogger(__name__)
    logger.info("Starting pyglet-readme application")
    if args.verbose:
        logger.debug("Verbose mode enabled")
    if log_file:
        logger.info(f"Logging to file: {log_file}")

    try:
        run_hello_world()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
