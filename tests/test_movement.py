"""Unit tests for movement utility functions.

Tests pure functions for vector math, keyboard input, mouse click handling,
and chase AI behavior.
"""

import math
import unittest

from pyglet_readme.movement import (
    Vector2,
    apply_speed_to_direction,
    apply_travel_distance,
    calculate_chase_velocity,
    calculate_click_velocity,
    calculate_keyboard_velocity,
    clamp_to_bounds,
    distance,
    is_moving,
    normalize_vector,
    update_position,
)


class TestDistance(unittest.TestCase):
    """Tests for distance calculation."""

    def test_distance_same_point(self) -> None:
        """Distance between same point should be zero."""
        self.assertEqual(distance(0, 0, 0, 0), 0.0)
        self.assertEqual(distance(5, 5, 5, 5), 0.0)

    def test_distance_horizontal(self) -> None:
        """Distance between points on same horizontal line."""
        self.assertEqual(distance(0, 0, 3, 0), 3.0)
        self.assertEqual(distance(10, 5, 13, 5), 3.0)

    def test_distance_vertical(self) -> None:
        """Distance between points on same vertical line."""
        self.assertEqual(distance(0, 0, 0, 4), 4.0)
        self.assertEqual(distance(5, 10, 5, 14), 4.0)

    def test_distance_3_4_5_triangle(self) -> None:
        """Distance in a 3-4-5 right triangle."""
        self.assertAlmostEqual(distance(0, 0, 3, 4), 5.0)
        self.assertAlmostEqual(distance(0, 0, 4, 3), 5.0)

    def test_distance_negative_coordinates(self) -> None:
        """Distance works with negative coordinates."""
        self.assertAlmostEqual(distance(-1, -1, 2, 3), 5.0)
        self.assertEqual(distance(-5, 0, 5, 0), 10.0)


class TestNormalizeVector(unittest.TestCase):
    """Tests for vector normalization."""

    def test_normalize_zero_vector(self) -> None:
        """Normalizing zero vector returns zero."""
        result = normalize_vector(0, 0)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_normalize_unit_vector(self) -> None:
        """Normalizing a unit vector should return itself."""
        result = normalize_vector(1, 0)
        self.assertAlmostEqual(result.x, 1.0)
        self.assertAlmostEqual(result.y, 0.0)

    def test_normalize_scales_to_unit_length(self) -> None:
        """Normalized vector should have length 1."""
        result = normalize_vector(3, 4)
        length = math.sqrt(result.x * result.x + result.y * result.y)
        self.assertAlmostEqual(length, 1.0)

    def test_normalize_3_4_5_triangle(self) -> None:
        """Normalize a 3-4-5 triangle."""
        result = normalize_vector(3, 4)
        self.assertAlmostEqual(result.x, 0.6)
        self.assertAlmostEqual(result.y, 0.8)

    def test_normalize_preserves_direction(self) -> None:
        """Normalized vector points in same direction."""
        result = normalize_vector(5, 0)
        self.assertGreater(result.x, 0)
        self.assertEqual(result.y, 0)

        result = normalize_vector(0, -5)
        self.assertEqual(result.x, 0)
        self.assertLess(result.y, 0)

    def test_normalize_negative_values(self) -> None:
        """Normalize handles negative values."""
        result = normalize_vector(-3, -4)
        length = math.sqrt(result.x * result.x + result.y * result.y)
        self.assertAlmostEqual(length, 1.0)


class TestApplySpeedToDirection(unittest.TestCase):
    """Tests for applying speed to a direction vector."""

    def test_apply_speed_to_unit_vector(self) -> None:
        """Apply speed to normalized direction."""
        result = apply_speed_to_direction(1, 0, 10)
        self.assertEqual(result, Vector2(10.0, 0.0))

    def test_apply_speed_zero_direction(self) -> None:
        """Zero direction with speed returns zero."""
        result = apply_speed_to_direction(0, 0, 10)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_apply_speed_diagonal(self) -> None:
        """Apply speed to diagonal direction."""
        result = apply_speed_to_direction(0.6, 0.8, 10)
        self.assertAlmostEqual(result.x, 6.0)
        self.assertAlmostEqual(result.y, 8.0)

    def test_apply_speed_negative_speed(self) -> None:
        """Negative speed reverses direction."""
        result = apply_speed_to_direction(1, 0, -10)
        self.assertEqual(result, Vector2(-10.0, 0.0))


class TestCalculateKeyboardVelocity(unittest.TestCase):
    """Tests for keyboard input velocity calculation."""

    def test_no_input(self) -> None:
        """No keys pressed returns zero velocity."""
        result = calculate_keyboard_velocity(False, False, False, False, 100)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_single_direction_up(self) -> None:
        """Up key only."""
        result = calculate_keyboard_velocity(True, False, False, False, 100)
        self.assertEqual(result, Vector2(0.0, 100.0))

    def test_single_direction_down(self) -> None:
        """Down key only."""
        result = calculate_keyboard_velocity(False, True, False, False, 100)
        self.assertEqual(result, Vector2(0.0, -100.0))

    def test_single_direction_left(self) -> None:
        """Left key only."""
        result = calculate_keyboard_velocity(False, False, True, False, 100)
        self.assertEqual(result, Vector2(-100.0, 0.0))

    def test_single_direction_right(self) -> None:
        """Right key only."""
        result = calculate_keyboard_velocity(False, False, False, True, 100)
        self.assertEqual(result, Vector2(100.0, 0.0))

    def test_opposite_directions_cancel(self) -> None:
        """Opposite directions cancel out."""
        result = calculate_keyboard_velocity(True, True, False, False, 100)
        self.assertEqual(result, Vector2(0.0, 0.0))

        result = calculate_keyboard_velocity(False, False, True, True, 100)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_diagonal_up_right(self) -> None:
        """Up + Right with default diagonal factor."""
        result = calculate_keyboard_velocity(True, False, False, True, 100)
        # Each should be speed * diagonal_factor (0.7071)
        expected_component = 100.0 * 0.7071
        self.assertAlmostEqual(result.x, expected_component, places=3)
        self.assertAlmostEqual(result.y, expected_component, places=3)

    def test_diagonal_down_left(self) -> None:
        """Down + Left with default diagonal factor."""
        result = calculate_keyboard_velocity(False, True, True, False, 100)
        expected_component = 100.0 * 0.7071
        self.assertAlmostEqual(result.x, -expected_component, places=3)
        self.assertAlmostEqual(result.y, -expected_component, places=3)

    def test_custom_diagonal_factor(self) -> None:
        """Diagonal factor can be customized."""
        result = calculate_keyboard_velocity(True, False, True, False, 100, diagonal_factor=0.5)
        self.assertAlmostEqual(result.x, -50.0)
        self.assertAlmostEqual(result.y, 50.0)


class TestCalculateClickVelocity(unittest.TestCase):
    """Tests for mouse click velocity calculation."""

    def test_click_same_position(self) -> None:
        """Click at current position returns zero velocity."""
        result = calculate_click_velocity(10, 10, 10, 10, 100)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_click_right(self) -> None:
        """Click to the right."""
        result = calculate_click_velocity(0, 0, 10, 0, 100)
        self.assertAlmostEqual(result.x, 100.0)
        self.assertAlmostEqual(result.y, 0.0)

    def test_click_diagonal(self) -> None:
        """Click diagonally."""
        result = calculate_click_velocity(0, 0, 3, 4, 10)
        # Normalized direction is (0.6, 0.8), apply speed 10
        self.assertAlmostEqual(result.x, 6.0)
        self.assertAlmostEqual(result.y, 8.0)

    def test_click_negative_coordinates(self) -> None:
        """Click from negative coordinates."""
        result = calculate_click_velocity(-10, -10, -7, -6, 10)
        # Direction: (3, 4), normalized: (0.6, 0.8)
        self.assertAlmostEqual(result.x, 6.0)
        self.assertAlmostEqual(result.y, 8.0)


class TestUpdatePosition(unittest.TestCase):
    """Tests for position update with velocity."""

    def test_no_velocity(self) -> None:
        """No velocity means no change."""
        result = update_position(10, 20, 0, 0, 1.0)
        self.assertEqual(result, Vector2(10.0, 20.0))

    def test_simple_movement(self) -> None:
        """Simple movement with unit velocity and time."""
        result = update_position(0, 0, 10, 20, 1.0)
        self.assertEqual(result, Vector2(10.0, 20.0))

    def test_movement_with_time_scale(self) -> None:
        """Movement scales with delta time."""
        result = update_position(0, 0, 10, 20, 0.5)
        self.assertEqual(result, Vector2(5.0, 10.0))

    def test_negative_velocity(self) -> None:
        """Negative velocity moves backward."""
        result = update_position(100, 100, -10, -20, 1.0)
        self.assertEqual(result, Vector2(90.0, 80.0))

    def test_fractional_time(self) -> None:
        """Fractional delta time (60Hz frame: 1/60)."""
        result = update_position(0, 0, 60, 120, 1 / 60)
        self.assertAlmostEqual(result.x, 1.0)
        self.assertAlmostEqual(result.y, 2.0)


class TestClampToBounds(unittest.TestCase):
    """Tests for position clamping to bounds."""

    def test_position_in_bounds(self) -> None:
        """Position already in bounds is unchanged."""
        result = clamp_to_bounds(50, 50, 200, 200, 10, 10)
        self.assertEqual(result, Vector2(50.0, 50.0))

    def test_clamp_left_edge(self) -> None:
        """Clamp to left edge."""
        result = clamp_to_bounds(-5, 50, 200, 200, 10, 10)
        self.assertEqual(result.x, 0.0)
        self.assertEqual(result.y, 50.0)

    def test_clamp_right_edge(self) -> None:
        """Clamp to right edge."""
        result = clamp_to_bounds(195, 50, 200, 200, 10, 10)
        self.assertEqual(result.x, 190.0)
        self.assertEqual(result.y, 50.0)

    def test_clamp_bottom_edge(self) -> None:
        """Clamp to bottom edge."""
        result = clamp_to_bounds(50, -5, 200, 200, 10, 10)
        self.assertEqual(result.x, 50.0)
        self.assertEqual(result.y, 0.0)

    def test_clamp_top_edge(self) -> None:
        """Clamp to top edge."""
        result = clamp_to_bounds(50, 195, 200, 200, 10, 10)
        self.assertEqual(result.x, 50.0)
        self.assertEqual(result.y, 190.0)

    def test_clamp_corner(self) -> None:
        """Clamp at corner."""
        result = clamp_to_bounds(-10, -10, 200, 200, 10, 10)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_clamp_accounts_for_sprite_size(self) -> None:
        """Sprite size affects clamping boundary."""
        # Sprite is 20x20 in 200x200 area
        result = clamp_to_bounds(185, 185, 200, 200, 20, 20)
        self.assertEqual(result.x, 180.0)
        self.assertEqual(result.y, 180.0)


class TestCalculateChaseVelocity(unittest.TestCase):
    """Tests for chase AI velocity calculation."""

    def test_chase_stationary_at_target(self) -> None:
        """At target (within threshold) returns zero velocity."""
        result = calculate_chase_velocity(10, 10, 10, 10, 100, distance_threshold=2.0)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_chase_within_threshold(self) -> None:
        """Distance less than threshold returns zero."""
        result = calculate_chase_velocity(10, 10, 11, 11, 100, distance_threshold=2.0)
        # sqrt(2) ≈ 1.41 < 2.0
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_chase_beyond_threshold(self) -> None:
        """Distance beyond threshold returns movement."""
        result = calculate_chase_velocity(0, 0, 3, 4, 10, distance_threshold=1.0)
        # Direction: (0.6, 0.8), speed: 10
        self.assertAlmostEqual(result.x, 6.0)
        self.assertAlmostEqual(result.y, 8.0)

    def test_chase_high_threshold(self) -> None:
        """Large threshold prevents movement."""
        result = calculate_chase_velocity(0, 0, 100, 100, 10, distance_threshold=1000.0)
        self.assertEqual(result, Vector2(0.0, 0.0))

    def test_chase_custom_speed(self) -> None:
        """Chase respects custom speed."""
        result = calculate_chase_velocity(0, 0, 3, 4, 20, distance_threshold=1.0)
        self.assertAlmostEqual(result.x, 12.0)
        self.assertAlmostEqual(result.y, 16.0)


class TestApplyTravelDistance(unittest.TestCase):
    """Tests for fixed-distance movement toward target."""

    def test_travel_distance_less_than_target(self) -> None:
        """Travel distance less than distance to target."""
        result = apply_travel_distance(0, 0, 10, 0, 3)
        self.assertAlmostEqual(result.x, 3.0)
        self.assertAlmostEqual(result.y, 0.0)

    def test_travel_distance_more_than_target(self) -> None:
        """Travel distance more than distance to target stops at target."""
        result = apply_travel_distance(0, 0, 3, 4, 100)
        self.assertAlmostEqual(result.x, 3.0)
        self.assertAlmostEqual(result.y, 4.0)

    def test_travel_distance_zero(self) -> None:
        """Zero travel distance means no movement."""
        result = apply_travel_distance(10, 10, 20, 20, 0)
        self.assertEqual(result, Vector2(10.0, 10.0))

    def test_travel_distance_to_same_position(self) -> None:
        """Travel distance when already at target."""
        result = apply_travel_distance(10, 10, 10, 10, 5)
        self.assertEqual(result, Vector2(10.0, 10.0))

    def test_travel_distance_diagonal(self) -> None:
        """Travel distance toward diagonal target."""
        result = apply_travel_distance(0, 0, 3, 4, 2.5)
        # Distance to target is 5, travel 2.5 which is 50%
        self.assertAlmostEqual(result.x, 1.5)
        self.assertAlmostEqual(result.y, 2.0)


class TestIsMoving(unittest.TestCase):
    """Tests for movement state detection."""

    def test_is_moving_at_target(self) -> None:
        """At target is not moving."""
        result = is_moving(10, 10, 10, 10, distance_threshold=2.0)
        self.assertFalse(result)

    def test_is_moving_within_threshold(self) -> None:
        """Within threshold is not moving."""
        result = is_moving(10, 10, 11, 11, distance_threshold=2.0)
        # sqrt(2) ≈ 1.41 < 2.0
        self.assertFalse(result)

    def test_is_moving_beyond_threshold(self) -> None:
        """Beyond threshold is moving."""
        result = is_moving(0, 0, 3, 4, distance_threshold=1.0)
        # Distance is 5 > 1.0
        self.assertTrue(result)

    def test_is_moving_exactly_threshold(self) -> None:
        """Exactly at threshold is not moving (uses >)."""
        result = is_moving(0, 0, 2, 0, distance_threshold=2.0)
        # Distance is exactly 2.0, not > 2.0
        self.assertFalse(result)

    def test_is_moving_just_beyond_threshold(self) -> None:
        """Just beyond threshold is moving."""
        result = is_moving(0, 0, 2.1, 0, distance_threshold=2.0)
        self.assertTrue(result)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions."""

    def test_keyboard_movement_in_bounds(self) -> None:
        """Keyboard movement respects bounds."""
        # Move right with keyboard
        velocity = calculate_keyboard_velocity(False, False, False, True, 100)
        new_pos = update_position(190, 50, velocity.x, velocity.y, 0.1)
        # Should move 10 pixels right
        self.assertAlmostEqual(new_pos.x, 200.0)

        # Clamp to bounds
        clamped = clamp_to_bounds(new_pos.x, new_pos.y, 200, 200, 10, 10)
        self.assertEqual(clamped.x, 190.0)

    def test_chase_sequence(self) -> None:
        """Chase AI with multiple frame updates."""
        # Start at (0, 0), chase target at (3, 4)
        x, y = 0.0, 0.0
        distance_threshold = 1.0
        speed = 10.0

        # First frame: velocity toward target
        velocity = calculate_chase_velocity(x, y, 3, 4, speed, distance_threshold)
        self.assertGreater(velocity.x, 0)
        self.assertGreater(velocity.y, 0)

        # Move one frame (0.5 seconds)
        new_pos = update_position(x, y, velocity.x, velocity.y, 0.5)
        x, y = new_pos.x, new_pos.y

        # Should be closer to target
        new_distance = distance(x, y, 3, 4)
        original_distance = distance(0, 0, 3, 4)
        self.assertLess(new_distance, original_distance)

    def test_click_to_bounds(self) -> None:
        """Click movement with bounds checking."""
        # Click far to right
        velocity = calculate_click_velocity(100, 100, 500, 100, 200)
        # Move one frame
        new_pos = update_position(100, 100, velocity.x, velocity.y, 0.1)
        # Clamp to window
        clamped = clamp_to_bounds(new_pos.x, new_pos.y, 200, 200, 10, 10)
        # Should be within bounds
        self.assertGreaterEqual(clamped.x, 0)
        self.assertLessEqual(clamped.x, 190)


if __name__ == "__main__":
    unittest.main()
