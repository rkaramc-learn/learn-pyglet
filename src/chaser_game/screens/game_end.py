"""Game end screen for showing win/loss conditions.

Displays final outcome, game statistics, and provides options to replay or quit the game.
"""

import logging

from pyglet.text import document, layout
from pyglet.window import key

from ..config import CONFIG
from ..types import WindowProtocol
from ..ui.primitives import Panel, StyledLabel
from .base import ScreenProtocol

logger = logging.getLogger(__name__)

# Game End Messages
MESSAGE_WIN = "You Win!!"
MESSAGE_LOSE = "Caught!"


# Helper to format RGB to Hex
def _rgb_to_hex(color_tuple: tuple[int, int, int]) -> str:
    return f"#{color_tuple[0]:02x}{color_tuple[1]:02x}{color_tuple[2]:02x}"


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

        # Background
        self.background_panel = Panel(
            x=0,
            y=0,
            width=window.width,
            height=window.height,
            color=CONFIG.COLOR_BACKGROUND,
        )

        # Outcome title (SVG Logo 75% scale)
        from ..ui.logo import ChaserLogo

        self.logo = ChaserLogo(x=window.width // 2, y=window.height - 120, scale=1.0)

        # Status Label (Win/Loss) - Initialized empty
        # We use a FormattedDocument to allow mixed colors while strictly adhering to points sizing
        self.status_doc = document.FormattedDocument("")
        self.status_layout = layout.TextLayout(
            self.status_doc, width=window.width, multiline=True, wrap_lines=False
        )
        self.status_layout.x = 0
        self.status_layout.y = window.height - 180
        self.status_layout.anchor_x = "left"  # We will center align text within the document
        self.status_layout.anchor_y = "center"

        # Statistics display (Minimalist floating text)
        self.stats_label = StyledLabel(
            "",
            font_size=14,
            color=(CONFIG.COLOR_TEXT.r, CONFIG.COLOR_TEXT.g, CONFIG.COLOR_TEXT.b, 200),
            x=window.width // 2,
            y=window.height // 2,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=window.width - 40,
            align="center",
        )

        # Replay prompt
        self.replay_label = StyledLabel(
            "press space to play again",
            font_size=CONFIG.FONT_SIZE_TITLE,
            color=(
                CONFIG.COLOR_GREEN_ACCENT.r,
                CONFIG.COLOR_GREEN_ACCENT.g,
                CONFIG.COLOR_GREEN_ACCENT.b,
                255,
            ),
            x=window.width // 2,
            y=150,
            anchor_x="center",
            anchor_y="center",
        )

        # Quit prompt
        self.quit_label = StyledLabel(
            "q to quit",
            font_size=CONFIG.FONT_SIZE_LABEL,
            color=(
                CONFIG.COLOR_TEXT_SECONDARY.r,
                CONFIG.COLOR_TEXT_SECONDARY.g,
                CONFIG.COLOR_TEXT_SECONDARY.b,
                150,
            ),
            x=window.width // 2,
            y=50,
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

        # Outcome Text
        # The Custom SVG Logo handles the "CHASER" branding.
        # However, the user request for "escaped!" vs "caught." logic needs to be addressed.
        # Wait, the user asked for "caught." / "escaped!" text previously, but now asked for the Logo.
        # "On end screen, size should be scaled down to 75%."
        # If the Logo says "CHASER", we still need the outcome state text.

        # Re-adding the outcome text below the logo, but removing the overlapping CHASER text if any.
        # The previous 'outcome_label' was the main title text.
        # Let's create a NEW label for the status message "caught." / "escaped!" below the logo.

        if is_win:
            raw_text = "escaped!"
            accent_color = (
                CONFIG.COLOR_GREEN_ACCENT.r,
                CONFIG.COLOR_GREEN_ACCENT.g,
                CONFIG.COLOR_GREEN_ACCENT.b,
                255,
            )
        else:
            raw_text = "caught."
            accent_color = (
                CONFIG.COLOR_RED_ACCENT.r,
                CONFIG.COLOR_RED_ACCENT.g,
                CONFIG.COLOR_RED_ACCENT.b,
                255,
            )

        self.status_doc.text = raw_text

        # Base Style (White, Header Size, Centered)
        self.status_doc.set_style(
            0,
            len(raw_text),
            {
                "font_name": CONFIG.FONT_NAME,
                "font_size": CONFIG.FONT_SIZE_HEADER,
                "color": (255, 255, 255, 255),
                "align": "center",
            },
        )

        # Accent Style for last character
        self.status_doc.set_style(
            len(raw_text) - 1,
            len(raw_text),
            {"color": accent_color},
        )

        # Format statistics
        minutes = int(self.time_survived) // 60
        seconds = int(self.time_survived) % 60
        distance_rounded = round(self.distance_traveled)

        stats_text = f"time survived: {minutes}m {seconds}s\ndistance run: {distance_rounded}px"
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
        pass

    def draw(self) -> None:
        """Render game end screen content."""
        self.background_panel.draw()
        self.logo.draw()
        self.status_layout.draw()
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
            from . import ScreenName

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenName.GAME_RUNNING)
        elif symbol == key.Q:
            logger.info("Quit requested from game end screen")
            self.window.close()
