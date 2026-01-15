"""Input handling system for entity control."""

from typing import Any, Protocol

from pyglet.window import key, mouse


class ControllableEntity(Protocol):
    """Protocol for entities that can be controlled via input."""

    def update_from_keyboard(self, up: bool, down: bool, left: bool, right: bool) -> None:
        """Update velocity from keyboard state."""
        ...

    def set_velocity_to_target(self, target_x: float, target_y: float) -> None:
        """Set velocity toward a target position."""
        ...

    def stop(self) -> None:
        """Stop all movement."""
        ...


def handle_keyboard_input(entity: ControllableEntity, keys: Any) -> None:
    """Handle continuous keyboard input for the mouse entity.

    Args:
        entity: Mouse entity to control.
        keys: pyglet KeyStateHandler instance with key states.
    """
    try:
        up = keys[key.UP]
        down = keys[key.DOWN]
        left = keys[key.LEFT]
        right = keys[key.RIGHT]
        entity.update_from_keyboard(up, down, left, right)
    except (KeyError, TypeError):
        # If keys doesn't support key lookup, skip
        pass


def handle_key_press(entity: ControllableEntity, symbol: int) -> None:
    """Handle discrete key press events.

    Maps special keys to movement commands.

    Args:
        entity: Mouse entity to control.
        symbol: Key symbol from pyglet.window.key.
    """
    # Diagonal directional keys
    if symbol == key.HOME:  # Up-Left
        entity.update_from_keyboard(up=True, down=False, left=True, right=False)
    elif symbol == key.PAGEUP:  # Up-Right
        entity.update_from_keyboard(up=True, down=False, left=False, right=True)
    elif symbol == key.END:  # Down-Left
        entity.update_from_keyboard(up=False, down=True, left=True, right=False)
    elif symbol == key.PAGEDOWN:  # Down-Right
        entity.update_from_keyboard(up=False, down=True, left=False, right=True)
    elif symbol == key.SPACE:  # Stop
        entity.stop()


def handle_mouse_press(entity: ControllableEntity, x: float, y: float, button: int) -> None:
    """Handle mouse click input.

    Args:
        entity: Mouse entity to control.
        x: Click x coordinate.
        y: Click y coordinate.
        button: Mouse button from pyglet.window.mouse.
    """
    if button == mouse.LEFT:
        entity.set_velocity_to_target(x, y)
