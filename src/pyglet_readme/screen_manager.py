"""Screen manager for handling screen transitions and lifecycle.

Manages the active screen, routes input events, and orchestrates screen updates and rendering.
"""

import logging
from typing import Any, Optional

from .screens.base import Screen
from .types import WindowProtocol

logger = logging.getLogger(__name__)


class ScreenManager:
    """Manages screen transitions and lifecycle.

    Keeps track of registered screens, maintains the active screen, and handles
    routing of update/draw/input calls to the active screen.
    """

    def __init__(self, window: WindowProtocol) -> None:
        """Initialize screen manager.

        Args:
            window: The pyglet game window instance.
        """
        self.window = window
        self.screens: dict[str, Screen] = {}
        self.active_screen: Optional[Screen] = None
        self.active_screen_name: Optional[str] = None

    def register_screen(self, name: str, screen: Screen) -> None:
        """Register a screen in the manager.

        Args:
            name: Unique screen identifier (e.g., "splash", "game_start", "game_running")
            screen: Screen instance to register
        """
        if name in self.screens:
            logger.warning(f"Screen '{name}' already registered, replacing")
        self.screens[name] = screen
        logger.debug(f"Registered screen: {name}")

    def set_active_screen(self, name: str) -> None:
        """Transition to a different screen.

        Calls on_exit() on the current screen and on_enter() on the new screen.

        Args:
            name: Name of the screen to activate

        Raises:
            ValueError: If the screen name is not registered
        """
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' not registered")

        # Exit current screen
        if self.active_screen:
            logger.debug(f"Exiting screen: {self.active_screen_name}")
            self.active_screen.on_exit()

        # Enter new screen
        self.active_screen = self.screens[name]
        self.active_screen_name = name
        logger.info(f"Transitioning to screen: {name}")
        if self.active_screen:
            self.active_screen.on_enter()

    def update(self, dt: float) -> None:
        """Update active screen.

        Args:
            dt: Time elapsed since last update in seconds
        """
        if self.active_screen:
            self.active_screen.update(dt)

    def draw(self) -> None:
        """Draw active screen.

        Should be called after window.clear() in the on_draw event.
        """
        if self.active_screen:
            self.active_screen.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Route key press to active screen.

        Args:
            symbol: Key symbol
            modifiers: Modifier keys
        """
        if self.active_screen:
            self.active_screen.on_key_press(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Route mouse press to active screen.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button
            modifiers: Modifier keys
        """
        if self.active_screen:
            self.active_screen.on_mouse_press(x, y, button, modifiers)
