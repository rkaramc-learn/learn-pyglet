"""Game end screen for showing win/loss conditions.

Displays final outcome and provides options to replay or quit the game.
"""

import logging
from typing import TYPE_CHECKING

import pyglet
from pyglet.window import key

from .base import Screen

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Game End Messages
MESSAGE_WIN = "You Win!!"
MESSAGE_LOSE = "Caught!"


class GameEndScreen(Screen):
    """Screen displayed when the game ends (win or loss).

    Shows the outcome message and provides options to replay or quit.
    """

    def __init__(self, window: "pyglet.window.Window") -> None:  # type: ignore[name-defined]
        """Initialize game end screen.

        Args:
            window: The pyglet game window instance.
        """
        super().__init__(window)

        # Outcome (set via set_outcome)
        self.is_win = False

        # Outcome title
        self.outcome_label = pyglet.text.Label(
            MESSAGE_WIN,
            font_name="Arial",
            font_size=72,
            x=window.width // 2,
            y=window.height - 150,
            anchor_x="center",
            anchor_y="center",
        )

        # Outcome description
        self.description_label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=20,
            x=window.width // 2,
            y=window.height // 2 + 100,
            anchor_x="center",
            anchor_y="center",
        )

        # Replay/Quit prompt
        self.prompt_label = pyglet.text.Label(
            "Press SPACE to Replay | Q to Quit",
            font_name="Arial",
            font_size=16,
            x=window.width // 2,
            y=100,
            anchor_x="center",
            anchor_y="center",
        )

    def set_outcome(self, is_win: bool) -> None:
        """Set the game outcome (win or loss).

        Args:
            is_win: True if player won, False if player lost.
        """
        self.is_win = is_win
        if is_win:
            self.outcome_label.text = MESSAGE_WIN
            self.description_label.text = "The kitten got tired and gave up!"
        else:
            self.outcome_label.text = MESSAGE_LOSE
            self.description_label.text = "The kitten caught you!"

    def on_enter(self) -> None:
        """Called when game end screen becomes active."""
        logger.info(f"Game end screen entered: {'win' if self.is_win else 'loss'}")

    def on_exit(self) -> None:
        """Called when game end screen is left."""
        logger.debug("Game end screen exited")

    def update(self, dt: float) -> None:
        """Update game end screen state.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        # No state changes needed for end screen

    def draw(self) -> None:
        """Render game end screen content."""
        self.outcome_label.draw()
        self.description_label.draw()
        self.prompt_label.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle key press events.

        Args:
            symbol: Key symbol
            modifiers: Modifier keys
        """
        if symbol == key.SPACE:
            logger.info("Replay requested from game end screen")
            # Import here to avoid circular imports
            from ..screen_manager import ScreenManager

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen("game_running")
        elif symbol == key.Q:
            logger.info("Quit requested from game end screen")
            self.window.close()
