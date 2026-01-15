"""Reusable UI primitives for the "Playful Chase" design system.

Provides high-level components like Panel, Button, and Label that abstract away
pyglet primitives and enforce consistent styling.
"""

from typing import Callable, Optional

import pyglet

from ..config import CONFIG


class Panel:
    """A styled container with background and optional border."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        color: tuple[int, int, int] = CONFIG.COLOR_BACKGROUND,
        opacity: int = 255,
        border_color: Optional[tuple[int, int, int]] = None,
        border_width: int = 2,
    ) -> None:
        """Initialize panel.

        Args:
            x: X coordinate (bottom-left)
            y: Y coordinate (bottom-left)
            width: Panel width
            height: Panel height
            color: Background RGB color
            opacity: Opacity (0-255)
            border_color: Optional border RGB color
            border_width: Width of border in pixels
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Main background shape
        self.background = pyglet.shapes.Rectangle(x, y, width, height, color=color)
        self.background.opacity = opacity

        # Border (implemented as a slightly larger rectangle behind if needed,
        # or separate lines. For simplicity/efficiency, we'll mimic border with
        # a larger rectangle behind if simple bordering isn't supported)
        self.border: Optional[pyglet.shapes.Rectangle] = None
        if border_color:
            self.border = pyglet.shapes.Rectangle(
                x - border_width,
                y - border_width,
                width + border_width * 2,
                height + border_width * 2,
                color=border_color,
            )
            self.border.opacity = opacity

    def draw(self) -> None:
        """Draw the panel."""
        if self.border:
            self.border.draw()
        self.background.draw()

    def update_position(self, x: float, y: float) -> None:
        """Update panel position."""
        dx = x - self.x
        dy = y - self.y
        self.x = x
        self.y = y

        self.background.x = x
        self.background.y = y

        if self.border:
            self.border.x += dx
            self.border.y += dy


class StyledLabel(pyglet.text.Label):
    """A label with default styling from the design system."""

    def __init__(
        self,
        text: str,
        font_size: int = CONFIG.FONT_SIZE_BODY,
        font_name: str = CONFIG.FONT_NAME,
        color: tuple[int, int, int, int] = (*CONFIG.COLOR_TEXT, 255),
        **kwargs,
    ) -> None:
        """Initialize styled label.

        Args:
            text: Label text
            font_size: Font size (defaults to body size)
            font_name: Font name (defaults to system config)
            color: RGBA color tuple
            **kwargs: Additional arguments passed to pyglet.text.Label
        """
        super().__init__(text, font_name=font_name, font_size=font_size, color=color, **kwargs)


class Button:
    """A clickable button with text and visual states."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        text: str,
        on_click: Optional[Callable[[], None]] = None,
        base_color: tuple[int, int, int] = CONFIG.COLOR_ACCENT,
        hover_color: tuple[int, int, int] = CONFIG.COLOR_PLAYER,
        text_color: tuple[int, int, int] = CONFIG.COLOR_TEXT,
    ) -> None:
        """Initialize button.

        Args:
            x: Center X coordinate
            y: Center Y coordinate
            width: Button width
            height: Button height
            text: Button label
            on_click: Callback function when clicked
            base_color: Normal state background color
            hover_color: Hover state background color
            text_color: Text color
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_click = on_click
        self.base_color = base_color
        self.hover_color = hover_color
        self.is_hovered = False

        # Calculate coordinates for centered rendering
        left = x - width / 2
        bottom = y - height / 2

        self.background = pyglet.shapes.Rectangle(left, bottom, width, height, color=base_color)

        self.label = StyledLabel(
            text,
            font_size=CONFIG.FONT_SIZE_BODY,
            x=x,
            y=y,
            anchor_x="center",
            anchor_y="center",
            color=(*text_color, 255),
        )

    def check_hit(self, x: float, y: float) -> bool:
        """Check if point is inside button bounds."""
        half_w = self.width / 2
        half_h = self.height / 2
        return self.x - half_w <= x <= self.x + half_w and self.y - half_h <= y <= self.y + half_h

    def on_mouse_motion(self, x: float, y: float) -> None:
        """Update hover state based on mouse position."""
        was_hovered = self.is_hovered
        self.is_hovered = self.check_hit(x, y)

        if self.is_hovered != was_hovered:
            self.background.color = self.hover_color if self.is_hovered else self.base_color

    def on_mouse_press(self, x: float, y: float, button: int) -> bool:
        """Handle mouse press. Returns True if clicked."""
        if self.check_hit(x, y) and self.on_click:
            self.on_click()
            return True
        return False

    def draw(self) -> None:
        """Draw the button."""
        self.background.draw()
        self.label.draw()
