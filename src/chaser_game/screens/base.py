"""Base screen class for game screens.

Each screen manages its own rendering, input handling, and state lifecycle.
"""

from abc import ABC, abstractmethod

from ..types import WindowProtocol


class Screen(ABC):
    """Abstract base class for game screens.

    Screens manage their own lifecycle (enter/exit), rendering, updates, and input handling.
    The screen manager calls these methods to orchestrate transitions and gameplay.
    """

    def __init__(self, window: WindowProtocol) -> None:
        """Initialize screen with reference to game window.

        Args:
            window: The pyglet game window instance.
        """
        self.window = window

    @abstractmethod
    def on_enter(self) -> None:
        """Called when screen becomes active.

        Initialize resources, start timers, reset state, etc.
        """

    @abstractmethod
    def on_exit(self) -> None:
        """Called when screen is being left.

        Clean up resources, stop timers, save state, etc.
        """

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update screen state.

        Args:
            dt: Time elapsed since last update in seconds.
        """

    @abstractmethod
    def draw(self) -> None:
        """Render screen content.

        Called after window.clear() by screen manager.
        Draw all sprites, text, shapes, etc. for this screen.
        """

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle key press events.

        Override to handle keyboard input. Called by screen manager if screen is active.

        Args:
            symbol: Key symbol (from pyglet.window.key)
            modifiers: Modifier keys pressed (from pyglet.window.key modifiers)
        """

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Handle mouse press events.

        Override to handle mouse input. Called by screen manager if screen is active.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button (pyglet.window.mouse)
            modifiers: Modifier keys pressed
        """
