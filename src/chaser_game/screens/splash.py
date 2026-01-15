"""Splash/intro screen for game startup.

Displays title/logo for a short duration then transitions to GameStart screen.
"""

import logging

import pyglet

from ..config import CONFIG
from ..types import WindowProtocol
from .base import ScreenProtocol

logger = logging.getLogger(__name__)


class SplashScreen(ScreenProtocol):
    """Splash screen shown at game startup.

    Displays title text for a configurable duration, then automatically
    transitions to the GameStart screen.
    """

    DISPLAY_DURATION = 2.0  # Seconds to show splash screen

    def __init__(self, window: WindowProtocol) -> None:
        """Initialize splash screen.

        Args:
            window: The pyglet game window instance.
        """
        super().__init__(window)
        self.elapsed_time = 0.0

        # Center coordinates
        cx = window.width // 2
        cy = window.height // 2

        # Main Title "CHASER"
        # Main Title "CHASER"
        from ..ui.logo import ChaserLogo

        self.logo = ChaserLogo(x=cx, y=cy)

    def on_enter(self) -> None:
        """Called when splash screen becomes active."""
        self.elapsed_time = 0.0
        # Reset background color to configured default
        # (Though Panel usually handles this in other screens)
        logger.info(f"Splash screen started (duration: {self.DISPLAY_DURATION}s)")

    def on_exit(self) -> None:
        """Called when splash screen is left."""
        logger.debug("Splash screen exited")

    def update(self, dt: float) -> None:
        """Update splash screen state.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        self.elapsed_time += dt

        # Transition to GameStart after duration expires
        if self.elapsed_time >= self.DISPLAY_DURATION:
            logger.info("Splash screen duration expired, transitioning to game_start")
            # Import here to avoid circular imports
            from ..screen_manager import ScreenManager
            from . import ScreenNames

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenNames.GAME_START)

    def draw(self) -> None:
        """Render splash screen content."""
        # Clear/Fill background manually since we don't have a Panel here
        # (or rely on window clear color if set globally, but safe to draw a rect)
        pyglet.shapes.Rectangle(
            0, 0, self.window.width, self.window.height, color=CONFIG.COLOR_BACKGROUND
        ).draw()

        self.logo.draw()
