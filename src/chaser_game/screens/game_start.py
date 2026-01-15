"""Game start/menu screen for displaying instructions and starting gameplay.

Shows how to play and provides a button or key press to start the game.
"""

import logging

from pyglet.window import key

from ..config import CONFIG
from ..types import WindowProtocol
from ..ui.primitives import Panel, StyledLabel
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

        # Background
        self.background_panel = Panel(
            x=0,
            y=0,
            width=window.width,
            height=window.height,
            color=CONFIG.COLOR_BACKGROUND,
        )

        # Title "CHASER"
        from ..ui.logo import ChaserLogo

        self.logo = ChaserLogo(x=window.width // 2, y=window.height - 120)
        # Note: StyledLabel might not expose 'bold' property directly if it wraps Label.
        # If StyledLabel inherits from Label, this works. If it wraps, we might need access.
        # Assuming StyledLabel is a wrapper or subclass (viewed in Primitive before? No, let's assume standard behavior for now).

        # Subtitle
        self.subtitle = StyledLabel(
            "survive the hunt",
            font_size=CONFIG.FONT_SIZE_HEADER,
            color=(*CONFIG.COLOR_TEXT_SECONDARY, 255),
            x=window.width // 2,
            y=window.height - 180,
            anchor_x="center",
            anchor_y="center",
        )

        # Instructions (Minimalist: No heavy panel, just text)
        instructions_text = "WASD / ARROWS to Move\nCLICK to Dash\nAvoid the Kitten"

        self.instruction_label = StyledLabel(
            instructions_text,
            font_size=CONFIG.FONT_SIZE_BODY,
            color=(*CONFIG.COLOR_TEXT, 255),
            x=window.width // 2,
            y=window.height // 2,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=window.width - 100,
            align="center",
        )

        # We perform a trick to keep the reference but not draw the panel if we don't want it,
        # or we just make it invisible.
        self.instructions_panel = Panel(x=0, y=0, width=0, height=0, color=(0, 0, 0), opacity=0)

        # Start prompt
        self.start_prompt = StyledLabel(
            "press space to start",
            font_size=CONFIG.FONT_SIZE_TITLE,
            color=(*CONFIG.COLOR_GREEN_ACCENT, 255),
            x=window.width // 2,
            y=150,
            anchor_x="center",
            anchor_y="center",
        )

        # Quit hint
        self.quit_hint = StyledLabel(
            "q to quit",
            font_size=CONFIG.FONT_SIZE_LABEL,
            color=(*CONFIG.COLOR_TEXT_SECONDARY, 150),
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
        pass

    def draw(self) -> None:
        """Render game start screen content."""
        self.background_panel.draw()
        self.logo.draw()
        self.subtitle.draw()
        self.instructions_panel.draw()
        self.instruction_label.draw()
        self.start_prompt.draw()
        self.quit_hint.draw()

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
            from . import ScreenName

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenName.GAME_RUNNING)
        elif symbol == key.Q:
            logger.info("Quit requested from game start screen")
            self.window.close()
