"""Game end screen for showing win/loss conditions.

Displays final outcome, game statistics, and provides options to replay or quit the game.
"""

import logging

from pyglet.window import key

from ..config import CONFIG
from ..types import WindowProtocol
from ..ui.primitives import Panel, StyledLabel
from .base import ScreenProtocol

logger = logging.getLogger(__name__)

# Game End Messages
MESSAGE_WIN = "You Win!!"
MESSAGE_LOSE = "Caught!"


class GameEndScreen(ScreenProtocol):
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
        self.time_survived = 0.0
        self.distance_traveled = 0.0

        # Background Panel (Tint)
        self.background_panel = Panel(
            x=0, y=0, width=window.width, height=window.height, color=(0, 0, 0), opacity=200
        )

        # Stats Card Panel
        card_width = 400
        card_height = 300
        self.stats_panel = Panel(
            x=window.width // 2 - card_width // 2,
            y=window.height // 2 - card_height // 2,
            width=card_width,
            height=card_height,
            color=CONFIG.COLOR_BACKGROUND,
            border_color=CONFIG.COLOR_ACCENT,
        )

        # Outcome title
        self.outcome_label = StyledLabel(
            MESSAGE_WIN,
            font_size=CONFIG.FONT_SIZE_HERO,
            x=window.width // 2,
            y=window.height // 2 + 100,
            anchor_x="center",
            anchor_y="center",
        )

        # Outcome description
        self.description_label = StyledLabel(
            "",
            font_size=CONFIG.FONT_SIZE_HEADER,
            x=window.width // 2,
            y=window.height // 2 + 40,
            anchor_x="center",
            anchor_y="center",
            color=(*CONFIG.COLOR_TEXT, 200),
        )

        # Statistics display
        self.stats_label = StyledLabel(
            "",
            font_size=CONFIG.FONT_SIZE_BODY,
            x=window.width // 2,
            y=window.height // 2 - 40,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=card_width - 40,
            align="center",
        )

        # Replay prompt (Visual Button)
        self.replay_label = StyledLabel(
            "PRESS [SPACE] TO PLAY AGAIN",
            font_size=CONFIG.FONT_SIZE_TITLE,
            color=(*CONFIG.COLOR_PLAYER, 255),
            x=window.width // 2,
            y=100,
            anchor_x="center",
            anchor_y="center",
        )

        # Quit prompt
        self.quit_label = StyledLabel(
            "Press Q to Quit",
            font_size=CONFIG.FONT_SIZE_LABEL,
            color=(*CONFIG.COLOR_ENEMY, 200),
            x=window.width // 2,
            y=40,
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

        # Set outcome text and themes
        if is_win:
            self.outcome_label.text = MESSAGE_WIN
            self.outcome_label.color = (*CONFIG.COLOR_PLAYER, 255)
            self.description_label.text = "You Outlasted the Kitten!"
            self.background_panel.background.color = (20, 50, 20)  # Greenish tint
            if self.stats_panel.border:
                self.stats_panel.border.color = CONFIG.COLOR_PLAYER
        else:
            self.outcome_label.text = MESSAGE_LOSE
            self.outcome_label.color = (*CONFIG.COLOR_ENEMY, 255)
            self.description_label.text = "Caught by the Kitten!"
            self.background_panel.background.color = (50, 20, 20)  # Reddish tint
            if self.stats_panel.border:
                self.stats_panel.border.color = CONFIG.COLOR_ENEMY

        # Format and display statistics
        self._update_stats_display()

    def _update_stats_display(self) -> None:
        """Update the statistics label with formatted game data."""
        # Format time (convert to minutes and seconds)
        minutes = int(self.time_survived) // 60
        seconds = int(self.time_survived) % 60

        # Format distance (show in pixels, rounded to nearest 10)
        distance_rounded = round(self.distance_traveled / 10) * 10

        stats_text = f"Time Survived: {minutes}m {seconds}s\nDistance Run: {distance_rounded}px"
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
        self.background_panel.draw()
        self.stats_panel.draw()
        self.outcome_label.draw()
        self.description_label.draw()
        self.stats_label.draw()
        self.replay_label.draw()
        self.quit_label.draw()

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
            from . import ScreenNames

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenNames.GAME_RUNNING)
        elif symbol == key.Q:
            logger.info("Quit requested from game end screen")
            self.window.close()
