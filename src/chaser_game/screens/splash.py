"""Splash/intro screen for game startup.

Displays title/logo for a short duration then transitions to GameStart screen.
"""

import logging

import pyglet
from pyglet.math import Vec2

from ..config import CONFIG
from ..movement import smooth_step
from ..types import WindowProtocol
from .base import ScreenProtocol

logger = logging.getLogger(__name__)


class SplashScreen(ScreenProtocol):
    """Splash screen shown at game startup.

    Displays title text for a configurable duration, then automatically
    transitions to the GameStart screen.
    """

    DISPLAY_DURATION = 2.5  # Seconds to show splash screen (Total animation time)

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

        # Animation State
        self.start_pos = Vec2(cx, cy)
        self.target_pos = Vec2(cx, window.height - 120)  # Target matches GameStartScreen
        self.current_pos = Vec2(cx, cy)

        # Start invisible
        self.logo.update_opacity(0)

    def on_enter(self) -> None:
        """Called when splash screen becomes active."""
        self.elapsed_time = 0.0
        # Reset background color to configured default
        # (Though Panel usually handles this in other screens)

        # Reset Animation State
        self.elapsed_time = 0.0
        self.current_pos = self.start_pos
        self.logo.update_position(self.start_pos.x, self.start_pos.y)
        self.logo.update_opacity(0)

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

        # Animation Phases

        # Phase 1: Fade In (0.0s - 1.0s)
        if self.elapsed_time <= 1.0:
            fade_progress = self.elapsed_time / 1.0
            opacity = int(smooth_step(fade_progress) * 255)
            self.logo.update_opacity(opacity)
            self.logo.update_position(self.start_pos.x, self.start_pos.y)

        # Phase 2: Hold (1.0s - 1.5s)
        elif self.elapsed_time <= 1.5:
            self.logo.update_opacity(255)
            self.logo.update_position(self.start_pos.x, self.start_pos.y)

        # Phase 3: Slide Up (1.5s - 2.5s)
        elif self.elapsed_time <= self.DISPLAY_DURATION:
            self.logo.update_opacity(255)
            # Normalize time for this phase (0.0 to 1.0 over 1 second)
            slide_progress = (self.elapsed_time - 1.5) / 1.0
            # Ease the progress
            t = smooth_step(slide_progress)
            # Lerp position
            self.current_pos = self.start_pos.lerp(self.target_pos, t)
            self.logo.update_position(self.current_pos.x, self.current_pos.y)

        # Transition to GameStart after duration expires
        if self.elapsed_time >= self.DISPLAY_DURATION:
            logger.info("Splash screen duration expired, transitioning to game_start")
            # Import here to avoid circular imports
            from ..screen_manager import ScreenManager
            from . import ScreenName

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenName.GAME_START)

    def draw(self) -> None:
        """Render splash screen content."""
        # Clear/Fill background manually since we don't have a Panel here
        # (or rely on window clear color if set globally, but safe to draw a rect)
        pyglet.shapes.Rectangle(
            0, 0, self.window.width, self.window.height, color=CONFIG.COLOR_BACKGROUND
        ).draw()

        self.logo.draw()
