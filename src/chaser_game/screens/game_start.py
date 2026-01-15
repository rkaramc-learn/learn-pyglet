"""Game start/menu screen for displaying instructions and starting gameplay.

Shows how to play and provides a button or key press to start the game.
"""

import logging

import pyglet
from pyglet.window import key

from ..types import WindowProtocol
from .base import ScreenProtocol

logger = logging.getLogger(__name__)


class GameStartScreen(ScreenProtocol):
    """Game start screen showing instructions and start prompt.

    Displays game title, controls, and waits for player to press SPACE or ENTER to begin.
    """

    def __init__(self, window: WindowProtocol) -> None:
        """Initialize game start screen.

        Args:
            window: The pyglet game window instance.
        """
        super().__init__(window)

        # Title
        self.title = pyglet.text.Label(
            "pyglet-readme: Chase Game",
            font_name="Arial",
            font_size=48,
            x=window.width // 2,
            y=window.height - 100,
            anchor_x="center",
            anchor_y="center",
        )

        # Instructions
        instructions = [
            "OBJECTIVE: Evade the kitten for as long as possible!",
            "",
            "CONTROLS:",
            "Arrow Keys or WASD - Move the mouse",
            "Mouse Click - Move mouse to clicked location",
            "HOME/PAGEUP/END/PAGEDOWN - Move diagonally",
            "SPACE - Stop moving",
            "",
            "GAMEPLAY:",
            "Avoid the kitten who chases you",
            "Stay healthy to survive",
            "Kitten gets tired over time",
            "",
        ]

        self.instruction_label = pyglet.text.Label(
            "\n".join(instructions),
            font_name="Arial",
            font_size=14,
            x=window.width // 2,
            y=window.height // 2 + 50,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=window.width - 100,
        )

        # Start prompt
        self.start_prompt = pyglet.text.Label(
            "Press SPACE or ENTER to Start | Q to Quit",
            font_name="Arial",
            font_size=16,
            x=window.width // 2,
            y=50,
            anchor_x="center",
            anchor_y="center",
        )

    def on_enter(self) -> None:
        """Called when game start screen becomes active."""
        logger.info("Game start screen entered")

    def on_exit(self) -> None:
        """Called when game start screen is left."""
        logger.debug("Game start screen exited")

    def update(self, dt: float) -> None:
        """Update game start screen state.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        # No state changes needed for start screen

    def draw(self) -> None:
        """Render game start screen content."""
        self.title.draw()
        self.instruction_label.draw()
        self.start_prompt.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle key press events.

        Args:
            symbol: Key symbol
            modifiers: Modifier keys
        """
        if symbol in (key.SPACE, key.ENTER):
            logger.info("Start game requested")
            # Import here to avoid circular imports
            from ..screen_manager import ScreenManager
            from . import ScreenNames

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenNames.GAME_RUNNING)
        elif symbol == key.Q:
            logger.info("Quit requested from game start screen")
            self.window.close()
