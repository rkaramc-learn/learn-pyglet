#!/usr/bin/env python3
"""
End-to-End Test: Verify full game startup with new asset system.

This test verifies that:
1. The asset system is properly initialized
2. All required assets are found (or fallbacks are available)
3. The game window can be created
4. Core entities load without errors
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyglet_readme.assets import get_loader
from pyglet_readme.logging_config import get_logger, init_logging

logger = get_logger(__name__)


def test_asset_system() -> None:
    """Test asset loader initialization and asset verification."""
    logger.info("Testing asset system...")
    loader = get_loader()

    # Check that required assets are specified
    required_assets = {
        "assets/images/kitten.png": "image",
        "assets/sprites/mouse_sheet.png": "image",
        "assets/audio/sfx/meow.wav": "sound",
        "assets/audio/music/ambience.wav": "sound",
    }

    result = loader.verify_assets(required_assets)
    logger.debug(f"Asset verification result: {result}")

    # Verify critical assets are loadable
    try:
        kitten = loader.load_image("assets/images/kitten.png")
        logger.info(f"Kitten image loaded: {kitten.width}x{kitten.height}")
        assert kitten.width > 0 and kitten.height > 0
    except FileNotFoundError as e:
        logger.error(f"Failed to load kitten image: {e}")
        raise AssertionError(f"Failed to load kitten image: {e}") from e


def test_game_startup() -> None:
    """Test that game can initialize and start without crashing."""
    logger.info("Testing game startup...")

    import pyglet
    from pyglet_readme.hello_world import run_hello_world

    # Mock the run to prevent actual window creation
    original_run = pyglet.app.run

    def mock_run():
        """Immediately close instead of running."""
        logger.debug("Game window would start (mocked for testing)")

    pyglet.app.run = mock_run  # type: ignore[method-assign]

    try:
        # Call the startup - should not raise exceptions
        run_hello_world()
        logger.info("Game initialization successful")
    except Exception as e:
        logger.error(f"Game initialization failed: {e}")
        raise AssertionError(f"Game initialization failed: {e}") from e
    finally:
        pyglet.app.run = original_run


def main(verbosity: int = 0) -> int:
    """Run all E2E tests.

    Args:
        verbosity: Verbosity level (0=WARNING, 1=INFO, 2=DEBUG, 3+=TRACE).

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    from pyglet_readme.logging_config import TRACE_LEVEL

    # Determine log level based on verbosity
    if verbosity == 0:
        log_level = logging.WARNING
    elif verbosity == 1:
        log_level = logging.INFO
    elif verbosity == 2:
        log_level = logging.DEBUG
    else:
        log_level = TRACE_LEVEL

    init_logging(level=log_level)

    logger.info("=" * 60)
    logger.info("E2E Test: Full Game Startup with New Asset System")
    logger.info("=" * 60)

    tests = [
        ("Asset System", test_asset_system),
        ("Game Startup", test_game_startup),
    ]

    logger.info("Running test suite...")
    results = []

    for name, test_func in tests:
        try:
            test_func()
            logger.info(f"✓ {name} passed")
            results.append((name, True))
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}")
            results.append((name, False))

    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        logger.info(f"  [{status}] {name}")

    all_passed = all(passed for _, passed in results)
    logger.info("=" * 60)

    if all_passed:
        logger.info("All E2E tests PASSED")
        return 0
    else:
        logger.error("Some E2E tests FAILED")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E2E test for game startup")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity: -v (INFO), -vv (DEBUG), -vvv (TRACE)",
    )
    args = parser.parse_args()
    sys.exit(main(verbosity=args.verbose))
