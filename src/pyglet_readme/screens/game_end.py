"""Game end screen for showing win/loss conditions.

Displays final outcome, game statistics, and provides options to replay or quit the game.
"""

import logging

import pyglet
from pyglet.window import key

from ..types import WindowProtocol
from .base import Screen

logger = logging.getLogger(__name__)

# Game End Messages
MESSAGE_WIN = "You Win!!"
MESSAGE_LOSE = "Caught!"


class GameEndScreen(Screen):
    """Screen displayed when the game ends (win or loss).

    Shows the outcome message, game statistics, and provides options to replay or quit.
    """

    def __init__(self, window: WindowProtocol) -> None:
        """Initialize game end screen.

        Args:
            window: The pyglet game window instance.
        """
        super().__init__(window)

        # Outcome (set via set_outcome)
        self.is_win = False

        # Game statistics
        self.time_survived = 0.0  # Time in seconds
        self.distance_traveled = 0.0  # Pixels

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

        # Statistics display
        self.stats_label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=16,
            x=window.width // 2,
            y=window.height // 2 - 20,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=window.width - 100,
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

    def set_outcome(
        self, is_win: bool, time_survived: float = 0.0, distance_traveled: float = 0.0
    ) -> None:
        """Set the game outcome and statistics.

        Args:
            is_win: True if player won, False if player lost.
            time_survived: Time survived in seconds.
            distance_traveled: Distance traveled in pixels.
        """
        self.is_win = is_win
        self.time_survived = time_survived
        self.distance_traveled = distance_traveled

        # Set outcome text
        if is_win:
            self.outcome_label.text = MESSAGE_WIN
            self.description_label.text = "The kitten got tired and gave up!"
        else:
            self.outcome_label.text = MESSAGE_LOSE
            self.description_label.text = "The kitten caught you!"

        # Format and display statistics
        self._update_stats_display()

    def _update_stats_display(self) -> None:
        """Update the statistics label with formatted game data."""
        # Format time (convert to minutes and seconds)
        minutes = int(self.time_survived) // 60
        seconds = int(self.time_survived) % 60

        # Format distance (show in pixels, rounded to nearest 10)
        distance_rounded = round(self.distance_traveled / 10) * 10

        stats_text = f"Time Survived: {minutes}m {seconds}s\nDistance Traveled: {distance_rounded} pixels"
        self.stats_label.text = stats_text

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
        self.stats_label.draw()
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
