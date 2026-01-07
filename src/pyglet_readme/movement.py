"""Pure functions for vector math and movement logic.

This module provides testable utility functions for:
- Vector calculations (distance, normalization)
- Movement behavior (keyboard-based, chase AI, bounds clamping)
- Velocity calculations based on input

These functions are independent of game state and pygame/pyglet specifics,
making them ideal for unit testing.
"""

import math
from typing import NamedTuple


class Vector2(NamedTuple):
    """2D vector representation."""

    x: float
    y: float


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points.

    Args:
        x1: X coordinate of first point.
        y1: Y coordinate of first point.
        x2: X coordinate of second point.
        y2: Y coordinate of second point.

    Returns:
        Distance between the two points.
    """
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def normalize_vector(dx: float, dy: float) -> Vector2:
    """Normalize a vector to unit length.

    If the vector has zero length, returns (0, 0).

    Args:
        dx: X component of vector.
        dy: Y component of vector.

    Returns:
        Normalized vector as Vector2(x, y).
    """
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return Vector2(0.0, 0.0)
    return Vector2(dx / length, dy / length)


def apply_speed_to_direction(
    direction_x: float, direction_y: float, speed: float
) -> Vector2:
    """Apply speed magnitude to a direction vector.

    The direction should already be normalized. If it's not, this function
    will still work correctly.

    Args:
        direction_x: X component of direction (ideally normalized).
        direction_y: Y component of direction (ideally normalized).
        speed: Speed magnitude to apply.

    Returns:
        Velocity vector as Vector2(vx, vy).
    """
    return Vector2(direction_x * speed, direction_y * speed)


def calculate_keyboard_velocity(
    up: bool,
    down: bool,
    left: bool,
    right: bool,
    speed: float,
    diagonal_factor: float = 0.7071,
) -> Vector2:
    """Calculate velocity from keyboard input.

    Handles:
    - Cardinal directions (up, down, left, right)
    - Diagonal directions with proper normalization
    - No input (stationary)

    Args:
        up: True if up key is pressed.
        down: True if down key is pressed.
        left: True if left key is pressed.
        right: True if right key is pressed.
        speed: Movement speed magnitude.
        diagonal_factor: Normalization factor for diagonal movement (default: 1/sqrt(2)).

    Returns:
        Velocity vector as Vector2(vx, vy).
    """
    vx = 0.0
    vy = 0.0

    # Cardinal directions
    if up:
        vy += speed
    if down:
        vy -= speed
    if left:
        vx -= speed
    if right:
        vx += speed

    # Apply diagonal normalization if moving diagonally
    if (up or down) and (left or right):
        vx *= diagonal_factor
        vy *= diagonal_factor

    return Vector2(vx, vy)


def calculate_click_velocity(
    current_x: float,
    current_y: float,
    target_x: float,
    target_y: float,
    speed: float,
) -> Vector2:
    """Calculate velocity toward a click target.

    Args:
        current_x: Current x coordinate.
        current_y: Current y coordinate.
        target_x: Target x coordinate (click location).
        target_y: Target y coordinate (click location).
        speed: Movement speed magnitude.

    Returns:
        Velocity vector as Vector2(vx, vy). If already at target, returns (0, 0).
    """
    dx = target_x - current_x
    dy = target_y - current_y

    direction = normalize_vector(dx, dy)
    return apply_speed_to_direction(direction.x, direction.y, speed)


def update_position(
    x: float, y: float, vx: float, vy: float, dt: float
) -> Vector2:
    """Update position based on velocity and delta time.

    Args:
        x: Current x coordinate.
        y: Current y coordinate.
        vx: X velocity.
        vy: Y velocity.
        dt: Time elapsed in seconds.

    Returns:
        New position as Vector2(x, y).
    """
    return Vector2(x + vx * dt, y + vy * dt)


def clamp_to_bounds(
    x: float, y: float, bounds_width: float, bounds_height: float,
    sprite_width: float, sprite_height: float
) -> Vector2:
    """Clamp position to window bounds.

    Args:
        x: Current x coordinate.
        y: Current y coordinate.
        bounds_width: Width of the bounding area (window width).
        bounds_height: Height of the bounding area (window height).
        sprite_width: Width of the sprite being bounded.
        sprite_height: Height of the sprite being bounded.

    Returns:
        Clamped position as Vector2(x, y).
    """
    clamped_x = max(0.0, min(bounds_width - sprite_width, x))
    clamped_y = max(0.0, min(bounds_height - sprite_height, y))
    return Vector2(clamped_x, clamped_y)


def calculate_chase_velocity(
    current_x: float,
    current_y: float,
    target_x: float,
    target_y: float,
    speed: float,
    distance_threshold: float = 2.0,
) -> Vector2:
    """Calculate velocity to chase a target.

    If the distance to target is less than the threshold, returns zero velocity
    to prevent jitter from very small movements.

    Args:
        current_x: Current x coordinate.
        current_y: Current y coordinate.
        target_x: Target x coordinate.
        target_y: Target y coordinate.
        speed: Chase speed magnitude.
        distance_threshold: Minimum distance before moving (prevents jitter).

    Returns:
        Velocity vector as Vector2(vx, vy).
    """
    dist = distance(current_x, current_y, target_x, target_y)

    if dist <= distance_threshold:
        return Vector2(0.0, 0.0)

    direction = normalize_vector(target_x - current_x, target_y - current_y)
    return apply_speed_to_direction(direction.x, direction.y, speed)


def apply_travel_distance(
    current_x: float,
    current_y: float,
    target_x: float,
    target_y: float,
    travel_distance: float,
) -> Vector2:
    """Move a fixed distance toward a target.

    This is used for frame-rate-independent movement with a maximum travel per frame.

    Args:
        current_x: Current x coordinate.
        current_y: Current y coordinate.
        target_x: Target x coordinate.
        target_y: Target y coordinate.
        travel_distance: Maximum distance to travel this frame.

    Returns:
        New position as Vector2(x, y).
    """
    dist = distance(current_x, current_y, target_x, target_y)

    if dist == 0:
        return Vector2(current_x, current_y)

    direction = normalize_vector(target_x - current_x, target_y - current_y)
    step = min(travel_distance, dist)
    return Vector2(
        current_x + direction.x * step,
        current_y + direction.y * step,
    )


def is_moving(
    current_x: float,
    current_y: float,
    target_x: float,
    target_y: float,
    distance_threshold: float = 2.0,
) -> bool:
    """Check if movement is needed (distance exceeds threshold).

    Args:
        current_x: Current x coordinate.
        current_y: Current y coordinate.
        target_x: Target x coordinate.
        target_y: Target y coordinate.
        distance_threshold: Minimum distance to be considered "moving".

    Returns:
        True if distance > threshold, False otherwise.
    """
    return distance(current_x, current_y, target_x, target_y) > distance_threshold
