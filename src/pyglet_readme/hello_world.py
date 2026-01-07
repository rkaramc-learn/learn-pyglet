import logging

import pyglet

from .screen_manager import ScreenManager
from .screens.game_end import GameEndScreen
from .screens.game_start import GameStartScreen
from .screens.game_running import GameRunningScreen
from .screens.splash import SplashScreen

logger = logging.getLogger(__name__)


def run_hello_world() -> None:
    """Initialize and run the game application with multi-screen support."""

    logger.info("Starting game initialization")

    logger.info("Creating game window")
    window = pyglet.window.Window()
    logger.info(f"Window created: {window.width}x{window.height}")

    # Initialize screen manager
    screen_manager = ScreenManager(window)
    window._screen_manager = screen_manager  # type: ignore[attr-defined]

    # Create and register all screens
    splash_screen = SplashScreen(window)
    game_start_screen = GameStartScreen(window)
    game_running_screen = GameRunningScreen(window)
    game_end_screen = GameEndScreen(window)

    screen_manager.register_screen("splash", splash_screen)
    screen_manager.register_screen("game_start", game_start_screen)
    screen_manager.register_screen("game_running", game_running_screen)
    screen_manager.register_screen("game_end", game_end_screen)

    # Start with splash screen
    screen_manager.set_active_screen("splash")

    # Set up event handlers to route to screen manager
    @window.event  # type: ignore[attr-defined]
    def on_draw() -> None:  # type: ignore[no-untyped-def]
        window.clear()
        screen_manager.draw()

    @window.event  # type: ignore[attr-defined]
    def on_key_press(symbol: int, modifiers: int) -> None:  # type: ignore[no-untyped-def]
        screen_manager.on_key_press(symbol, modifiers)

    @window.event  # type: ignore[attr-defined]
    def on_mouse_press(x: int, y: int, button: int, modifiers: int) -> None:  # type: ignore[no-untyped-def]
        screen_manager.on_mouse_press(x, y, button, modifiers)

    def update(dt: float) -> None:
        screen_manager.update(dt)

    logger.info("Game initialization complete, starting game loop")
    pyglet.clock.schedule_interval(update, 1 / 60.0)  # type: ignore[attr-defined]

    logger.info("Starting game application")
    pyglet.app.run()
    logger.info("Game application closed")


if __name__ == "__main__":
    run_hello_world()
