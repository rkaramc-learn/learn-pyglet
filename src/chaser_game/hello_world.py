import logging

import pyglet

from .screen_manager import ScreenManager
from .screens import ScreenName
from .screens.game_end import GameEndScreen
from .screens.game_running import GameRunningScreen
from .screens.game_start import GameStartScreen
from .screens.splash import SplashScreen
from .types import WindowProtocol

logger = logging.getLogger(__name__)


def main(capture_screenshots: bool = False) -> None:
    """Initialize and run the game application with multi-screen support.

    Args:
        capture_screenshots: Whether to enable automated screenshot capture.
    """

    logger.info("Starting game initialization")

    logger.info("Creating game window")
    window: WindowProtocol = pyglet.window.Window()
    logger.info(f"Window created: {window.width}x{window.height}")

    # Initialize screen manager
    screen_manager = ScreenManager(window, capture_screenshots=capture_screenshots)
    # Store screen manager on window for access from screens
    # Use setattr to avoid type checker issues with dynamic attributes
    window._screen_manager = screen_manager  # pyright: ignore[reportAttributeAccessIssue]

    # Create and register all screens
    splash_screen = SplashScreen(window)
    game_start_screen = GameStartScreen(window)
    game_running_screen = GameRunningScreen(window)
    game_end_screen = GameEndScreen(window)

    screen_manager.register_screen(ScreenName.SPLASH, splash_screen)
    screen_manager.register_screen(ScreenName.GAME_START, game_start_screen)
    screen_manager.register_screen(ScreenName.GAME_RUNNING, game_running_screen)
    screen_manager.register_screen(ScreenName.GAME_END, game_end_screen)

    # Start with splash screen
    screen_manager.set_active_screen(ScreenName.SPLASH)

    # Set up event handlers to route to screen manager
    @window.event
    def on_draw() -> None:
        window.clear()
        screen_manager.draw()

    @window.event
    def on_key_press(symbol: int, modifiers: int) -> None:
        screen_manager.on_key_press(symbol, modifiers)

    @window.event
    def on_mouse_press(x: int, y: int, button: int, modifiers: int) -> None:
        screen_manager.on_mouse_press(x, y, button, modifiers)

    def update(dt: float) -> None:
        screen_manager.update(dt)

    logger.info("Game initialization complete, starting game loop")
    pyglet.clock.schedule_interval(update, 1 / 60.0)

    logger.info("Starting game application")
    pyglet.app.run()
    logger.info("Game application closed")


if __name__ == "__main__":
    main()
