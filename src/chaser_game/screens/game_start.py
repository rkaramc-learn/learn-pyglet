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

        # Title
        self.title = StyledLabel(
            "CHASER GAME",
            font_size=CONFIG.FONT_SIZE_HERO,
            color=(*CONFIG.COLOR_PLAYER, 255),
            x=window.width // 2,
            y=window.height - 100,
            anchor_x="center",
            anchor_y="center",
        )

        # Subtitle
        self.subtitle = StyledLabel(
            "Evade the kitten. Stay alive.",
            font_size=CONFIG.FONT_SIZE_HEADER,
            color=(*CONFIG.COLOR_ACCENT, 255),
            x=window.width // 2,
            y=window.height - 160,
            anchor_x="center",
            anchor_y="center",
        )

        # Instructions Panel
        panel_width = window.width - 200
        panel_height = 250
        panel_x = 100
        panel_y = window.height // 2 - 50

        self.instructions_panel = Panel(
            x=panel_x,
            y=panel_y,
            width=panel_width,
            height=panel_height,
            color=(0, 0, 0),
            opacity=100,  # Semi-transparent
            border_color=CONFIG.COLOR_ACCENT,
        )

        instructions = [
            "CONTROLS",
            "----------------",
            "ARROWS / WASD  : Move Mouse",
            "CLICK          : Dash to Point",
            "SPACE          : Stop Moving",
            "",
            "SURVIVAL TIPS",
            "----------------",
            "Health drains near kitten.",
            "Kitten gets tired if you run.",
        ]

        self.instruction_label = StyledLabel(
            "\n".join(instructions),
            font_size=CONFIG.FONT_SIZE_BODY,
            x=window.width // 2,
            y=window.height // 2 + 75,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=panel_width - 40,
            align="center",
        )

        # Start prompt
        self.start_prompt = StyledLabel(
            "PRESS [SPACE] TO START",
            font_size=CONFIG.FONT_SIZE_TITLE,
            color=(*CONFIG.COLOR_TEXT, 255),
            x=window.width // 2,
            y=80,
            anchor_x="center",
            anchor_y="center",
        )

        # Quit hint
        self.quit_hint = StyledLabel(
            "Press Q to Quit",
            font_size=CONFIG.FONT_SIZE_LABEL,
            color=(*CONFIG.COLOR_ENEMY, 200),
            x=window.width // 2,
            y=30,
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
        # Simple pulsing effect for start prompt
        # self.start_prompt.opacity = int(128 + 127 * abs(math.sin(time.time() * 2)))
        pass

    def draw(self) -> None:
        """Render game start screen content."""
        self.background_panel.draw()
        self.title.draw()
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
            from . import ScreenNames

            manager = getattr(self.window, "_screen_manager", None)
            if isinstance(manager, ScreenManager):
                manager.set_active_screen(ScreenNames.GAME_RUNNING)
        elif symbol == key.Q:
            logger.info("Quit requested from game start screen")
            self.window.close()
