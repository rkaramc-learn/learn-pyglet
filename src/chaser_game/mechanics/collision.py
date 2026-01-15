"""Collision detection and bounds checking system."""

from typing import Protocol

from ..movement import distance


class BoundedEntity(Protocol):
    """Protocol for entities that can be clamped to bounds."""

    center_x: float
    center_y: float
    width: float
    height: float

    def clamp_to_bounds(self, window_width: float, window_height: float) -> None:
        """Clamp entity position to window bounds."""
        ...


def clamp_entities_to_bounds(
    mouse: BoundedEntity,
    kitten: BoundedEntity,
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
    mouse.clamp_to_bounds(window_width, window_height)
    kitten.clamp_to_bounds(window_width, window_height)


def check_catch_condition(
    mouse: BoundedEntity,
    kitten: BoundedEntity,
    catch_range: float,
) -> bool:
    """Check if kitten has caught the mouse.

    Args:
        mouse: Mouse entity.
        kitten: Kitten entity.
        catch_range: Distance at which kitten catches mouse.

    Returns:
        True if kitten has caught the mouse, False otherwise.
    """
    dist = distance(mouse.center_x, mouse.center_y, kitten.center_x, kitten.center_y)
    return dist < catch_range
