"""Type protocols for duck typing and structural subtyping.

This module defines Protocol classes for pyglet types and other duck-typed interfaces
to enable proper type checking without circular imports or TYPE_CHECKING hacks.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class WindowProtocol(Protocol):
    """Protocol for pyglet.window.Window to enable duck typing.

    Represents the interface of a pyglet Window without direct imports,
    avoiding circular dependencies and TYPE_CHECKING issues.
    """

    @property
    def width(self) -> int:
        """Window width in pixels."""
        ...

    @property
    def height(self) -> int:
        """Window height in pixels."""
        ...

    def push_handlers(self, *args: Any, **kwargs: Any) -> None:
        """Push event handlers onto the window stack."""

    def pop_handlers(self) -> None:
        """Pop event handlers from the window stack."""

    def clear(self) -> None:
        """Clear the window (fill with background color)."""

    def close(self) -> None:
        """Close the window."""

    def event(self, *args: Any, **kwargs: Any) -> Any:
        """Decorator to register an event handler."""


class DrawableProtocol(Protocol):
    """Protocol for objects that can be drawn (pyglet.sprite.Sprite, pyglet.shapes)."""

    def draw(self) -> None:
        """Draw the object on screen."""


class AudioProtocol(Protocol):
    """Protocol for pyglet.media.Player audio playback interface."""

    loop: bool

    def play(self) -> None:
        """Start playback."""

    def pause(self) -> None:
        """Pause playback."""

    def queue(self, source: Any) -> None:
        """Queue an audio source for playback."""


class SoundProtocol(Protocol):
    """Protocol for pyglet.media.StaticSource sound effects."""

    def play(self) -> Any:
        """Play the sound and return a player."""
