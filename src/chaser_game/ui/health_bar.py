"""Health bar UI component for entity health/stamina visualization."""

import pyglet

from ..config import CONFIG


class HealthBar:
    """Reusable health/stamina bar UI component.

    Displays a filled bar (foreground) over a background bar, with color changes
    based on health/stamina thresholds.

    Attributes:
        background: Pyglet Rectangle shape for the background bar.
        foreground: Pyglet Rectangle shape for the filled portion.
        max_value: Maximum value for the bar (health or stamina cap).
    """

    def __init__(
        self,
        max_value: float = CONFIG.MAX_HEALTH,
        width: int = CONFIG.BAR_WIDTH,
        height: int = CONFIG.BAR_HEIGHT,
        x: float = 0.0,
        y: float = 0.0,
    ) -> None:
        """Initialize health bar.

        Args:
            max_value: Maximum value for the bar (default: MAX_HEALTH).
            width: Width of the bar in pixels.
            height: Height of the bar in pixels.
            x: Initial x position.
            y: Initial y position.
        """
        self.max_value = max_value
        self.width = width
        self.height = height

        # Background (empty) bar
        self.background = pyglet.shapes.Rectangle(
            x - 2,
            y - 2,
            width + 4,
            height + 4,
            color=CONFIG.COLOR_BACKGROUND,
        )
        # Border effect via background being larger
        self.background.opacity = 200

        # Foreground (filled) bar
        self.foreground = pyglet.shapes.Rectangle(
            x, y, width, height, color=CONFIG.COLOR_HEALTH_GOOD
        )

    def update(self, current_value: float, x: float, y: float) -> None:
        """Update bar position and fill based on current value.

        Args:
            current_value: Current health/stamina value (0 to max_value).
            x: New x position for the bar.
            y: New y position for the bar.
        """
        # Clamp value to valid range
        clamped_value = max(0.0, min(self.max_value, current_value))

        # Update background position (centered border effect)
        self.background.x = x - 2
        self.background.y = y - 2

        # Update foreground position and width
        self.foreground.x = x
        self.foreground.y = y
        self.foreground.width = self.width * (clamped_value / self.max_value)

        # Update color based on threshold
        if clamped_value > CONFIG.LOW_HEALTH_THRESHOLD:
            self.foreground.color = CONFIG.COLOR_HEALTH_GOOD
        elif clamped_value > 0:
            self.foreground.color = CONFIG.COLOR_HEALTH_LOW
        else:
            self.foreground.color = CONFIG.COLOR_HEALTH_CRITICAL

    def draw(self) -> None:
        """Draw both background and foreground bars."""
        self.background.draw()
        self.foreground.draw()

    def set_position(self, x: float, y: float) -> None:
        """Set bar position.

        Args:
            x: New x position.
            y: New y position.
        """
        self.background.x = x
        self.background.y = y
        self.foreground.x = x
        self.foreground.y = y

    def get_position(self) -> tuple[float, float]:
        """Get current bar position.

        Returns:
            Tuple of (x, y) position.
        """
        return (self.background.x, self.background.y)
