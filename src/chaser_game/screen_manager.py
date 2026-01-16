"""Screen manager for handling screen transitions and lifecycle.

Manages the active screen, routes input events, and orchestrates screen updates and rendering.
"""

import concurrent.futures
import datetime
import logging
import os
from typing import Optional

import pyglet

from .screens import ScreenName
from .screens.base import ScreenProtocol
from .types import WindowProtocol

logger = logging.getLogger(__name__)


class ScreenManager:
    """Manages screen transitions and lifecycle.

    Keeps track of registered screens, maintains the active screen, and handles
    routing of update/draw/input calls to the active screen.
    """

    def __init__(self, window: WindowProtocol, capture_screenshots: bool = False) -> None:
        """Initialize screen manager.

        Args:
            window: The pyglet game window instance.
            capture_screenshots: Whether to capture screenshots on screen transitions.
        """
        self.window = window
        self.screens: dict[str, ScreenProtocol] = {}
        self.active_screen: Optional[ScreenProtocol] = None
        self.active_screen_name: Optional[str] = None
        self.capture_screenshots = capture_screenshots

        # Screenshot state
        self._capture_next_frame: bool = False
        self._screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self._screenshot_dir, exist_ok=True)
        # Thread pool for offloading screenshot IO
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def register_screen(self, name: ScreenName, screen: ScreenProtocol) -> None:
        """Register a screen in the manager.

        Args:
            name: Unique screen identifier (e.g., "splash", "game_start", "game_running")
            screen: Screen instance to register
        """
        if name in self.screens:
            logger.warning(f"Screen '{name}' already registered, replacing")
        self.screens[name] = screen
        logger.debug(f"Registered screen: {name}")

    def _capture_screenshot(self, screen_name: str, event: str) -> None:
        """Capture and save a screenshot of the current frame.

        Args:
            screen_name: Name of the screen being captured
            event: Event name (e.g., 'enter', 'exit')
        """
        try:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            milliseconds = int(now.microsecond / 1000)
            filename = f"{timestamp}_{milliseconds:03d}_{screen_name}_{event}.png"
            path = os.path.join(self._screenshot_dir, filename)

            path = os.path.join(self._screenshot_dir, filename)

            # Get image data on main thread (fast, GL context required)
            image_data = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()

            # Offload saving (encoding + IO) to background thread
            self.executor.submit(image_data.save, path)
            logger.info(f"Queued screenshot save: {filename}")
        except Exception as e:
            logger.error(f"Failed to initiate screenshot capture: {e}")

    def set_active_screen(self, name: ScreenName) -> None:
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
            # Capture exit screenshot of the outgoing screen
            if self.capture_screenshots and self.active_screen_name:
                self._capture_screenshot(self.active_screen_name, "exit")
            self.active_screen.on_exit()

        # Enter new screen
        self.active_screen = self.screens[name]
        self.active_screen_name = name
        logger.info(f"Transitioning to screen: {name}")
        if self.active_screen:
            self.active_screen.on_enter()
            # Queue capture for the next frame (when it's drawn)
            if self.capture_screenshots:
                self._capture_next_frame = True

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

            # If queued, capture the frame we just drew
            if self._capture_next_frame and self.active_screen_name:
                self._capture_screenshot(self.active_screen_name, "enter")
                self._capture_next_frame = False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Route key press to active screen.

        Args:
            symbol: Key symbol
            modifiers: Modifier keys
        """
        # Global hotkeys
        if symbol == pyglet.window.key.INSERT:
            self._capture_screenshot(self.active_screen_name or "global", "manual")

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
