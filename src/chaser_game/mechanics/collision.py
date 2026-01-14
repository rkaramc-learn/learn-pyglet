"""Collision detection and bounds checking system."""

from typing import Any

from ..movement import distance

# TODO(pyglet-ciz.2): Update to use Protocol types for mouse/kitten entities


def clamp_entities_to_bounds(
    mouse: Any,
    kitten: Any,
    window_width: float,
    window_height: float,
) -> None:
    """Clamp both entities to window bounds.

    Args:
        mouse: Mouse entity to clamp.
        kitten: Kitten entity to clamp.
        window_width: Width of the game window.
        window_height: Height of the game window.
    """
    mouse.clamp_to_bounds(window_width, window_height, mouse.width, mouse.height)
    kitten.clamp_to_bounds(window_width, window_height, kitten.width, kitten.height)


def check_catch_condition(mouse: Any, kitten: Any, catch_range: float) -> bool:
    """Check if kitten has caught the mouse.

    Args:
        mouse: Mouse entity.
        kitten: Kitten entity.
        catch_range: Distance at which kitten catches mouse.

    Returns:
        True if kitten has caught the mouse, False otherwise.
    """
    mouse_center_x = mouse.x + mouse.width / 2
    mouse_center_y = mouse.y + mouse.height / 2
    kitten_center_x = kitten.x + kitten.width / 2
    kitten_center_y = kitten.y + kitten.height / 2

    dist = distance(mouse_center_x, mouse_center_y, kitten_center_x, kitten_center_y)
    return dist < catch_range
