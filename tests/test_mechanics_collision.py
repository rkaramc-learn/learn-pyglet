"""Tests for the mechanics.collision module."""

import unittest

from chaser_game.mechanics.collision import check_catch_condition, clamp_entities_to_bounds


class MockEntity:
    """Mock entity for testing collision functions."""

    def __init__(
        self,
        center_x: float = 0.0,
        center_y: float = 0.0,
        width: float = 32.0,
        height: float = 32.0,
    ) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self._clamped = False

    def clamp_to_bounds(self, window_width: float, window_height: float) -> None:
        """Mock clamp_to_bounds that records the call."""
        self._clamped = True
        half_width = self.width / 2
        half_height = self.height / 2
        self.center_x = max(half_width, min(window_width - half_width, self.center_x))
        self.center_y = max(half_height, min(window_height - half_height, self.center_y))


class TestClampEntitiesToBounds(unittest.TestCase):
    """Test the clamp_entities_to_bounds function."""

    def test_clamps_both_entities(self) -> None:
        """Test that both entities are clamped."""
        mouse = MockEntity(center_x=100.0, center_y=100.0)
        kitten = MockEntity(center_x=100.0, center_y=100.0)

        clamp_entities_to_bounds(mouse, kitten, 800.0, 600.0)

        self.assertTrue(mouse._clamped)
        self.assertTrue(kitten._clamped)

    def test_entity_outside_left_bound(self) -> None:
        """Test clamping entity outside left boundary."""
        mouse = MockEntity(center_x=-10.0, center_y=100.0)
        kitten = MockEntity(center_x=100.0, center_y=100.0)

        clamp_entities_to_bounds(mouse, kitten, 800.0, 600.0)

        # center_x should be clamped to half_width (16.0)
        self.assertEqual(mouse.center_x, 16.0)

    def test_entity_outside_right_bound(self) -> None:
        """Test clamping entity outside right boundary."""
        mouse = MockEntity(center_x=900.0, center_y=100.0)
        kitten = MockEntity(center_x=100.0, center_y=100.0)

        clamp_entities_to_bounds(mouse, kitten, 800.0, 600.0)

        # center_x should be clamped to (800 - 16) = 784
        self.assertEqual(mouse.center_x, 784.0)


class TestCheckCatchCondition(unittest.TestCase):
    """Test the check_catch_condition function."""

    def test_caught_at_same_position(self) -> None:
        """Test catch condition when entities overlap."""
        mouse = MockEntity(center_x=100.0, center_y=100.0)
        kitten = MockEntity(center_x=100.0, center_y=100.0)

        result = check_catch_condition(mouse, kitten, catch_range=50.0)

        self.assertTrue(result)

    def test_not_caught_when_far_apart(self) -> None:
        """Test no catch when entities are far apart."""
        mouse = MockEntity(center_x=0.0, center_y=0.0)
        kitten = MockEntity(center_x=500.0, center_y=500.0)

        result = check_catch_condition(mouse, kitten, catch_range=50.0)

        self.assertFalse(result)

    def test_caught_just_inside_range(self) -> None:
        """Test catch when just inside catch range."""
        mouse = MockEntity(center_x=0.0, center_y=0.0)
        kitten = MockEntity(center_x=49.0, center_y=0.0)

        result = check_catch_condition(mouse, kitten, catch_range=50.0)

        self.assertTrue(result)

    def test_not_caught_just_outside_range(self) -> None:
        """Test no catch when just outside catch range."""
        mouse = MockEntity(center_x=0.0, center_y=0.0)
        kitten = MockEntity(center_x=51.0, center_y=0.0)

        result = check_catch_condition(mouse, kitten, catch_range=50.0)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
