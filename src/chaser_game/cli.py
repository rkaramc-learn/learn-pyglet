import logging
import sys
from pathlib import Path

import click

from .hello_world import main
from .logging_config import TRACE_LEVEL, init_logging


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Interactive 2D game demonstrating pyglet library features."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(play)


@cli.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity: -v (INFO), -vv (DEBUG), -vvv (TRACE)",
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Write logs to file (default: no file logging)",
)
@click.option(
    "--screenshots/--no-screenshots",
    default=False,
    help="Enable/disable automated screenshot capture on screen transitions.",
)
@click.option(
    "--show-fps/--no-show-fps",
    default=False,
    help="Show/hide FPS counter overlay.",
)
def play(verbose: int, log_file: Path | None, screenshots: bool, show_fps: bool) -> None:
    """Start the game."""
    # Determine log level based on verbosity count
    if verbose == 0:
        log_level = logging.WARNING
    elif verbose == 1:
        log_level = logging.INFO
    elif verbose == 2:
        log_level = logging.DEBUG
    else:
        log_level = TRACE_LEVEL

    init_logging(level=log_level, log_file=log_file)

    logger = logging.getLogger(__name__)
    logger.warning("Starting pyglet-readme application via CLI")

    if verbose == 1:
        logger.info("Verbose mode (INFO level)")
    elif verbose == 2:
        logger.info("Very verbose mode (DEBUG level)")
    elif verbose >= 3:
        logger.info("Ultra verbose mode (TRACE level)")

    if log_file:
        logger.warning(f"Logging to file: {log_file}")

    try:
        main(capture_screenshots=screenshots, show_fps=show_fps)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
