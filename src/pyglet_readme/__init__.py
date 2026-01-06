import argparse
import logging
import sys
from pathlib import Path

from .hello_world import run_hello_world
from .logging_config import init_logging, TRACE_LEVEL


def main() -> None:
    """Entry point for the pyglet-readme application."""
    parser = argparse.ArgumentParser(
        description="Interactive 2D game demonstrating pyglet library features"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity: -v (INFO), -vv (DEBUG), -vvv (TRACE)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Write logs to file (default: no file logging)",
    )

    args = parser.parse_args()

    # Determine log level based on verbosity count
    # -v: INFO, -vv: DEBUG, -vvv: TRACE
    if args.verbose == 0:
        log_level = logging.WARNING  # Default
    elif args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose == 2:
        log_level = logging.DEBUG
    else:  # 3 or more
        log_level = TRACE_LEVEL

    log_file = Path(args.log_file) if args.log_file else None
    init_logging(level=log_level, log_file=log_file)

    logger = logging.getLogger(__name__)
    logger.warning("Starting pyglet-readme application")

    if args.verbose == 1:
        logger.info("Verbose mode (INFO level)")
    elif args.verbose == 2:
        logger.info("Very verbose mode (DEBUG level)")
    elif args.verbose >= 3:
        logger.info("Ultra verbose mode (TRACE level)")

    if log_file:
        logger.warning(f"Logging to file: {log_file}")

    try:
        run_hello_world()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
