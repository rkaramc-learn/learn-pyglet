"""Tests for the collision system."""

import unittest

from pyglet_readme.entities.kitten import Kitten
from pyglet_readme.entities.mouse import Mouse
from pyglet_readme.systems.collision import (
    check_catch_condition,
    clamp_entities_to_bounds,
)


class TestCollisionSystem(unittest.TestCase):
    """Test the collision detection system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mouse = Mouse(x=0.0, y=0.0)
        self.mouse.width = 32.0
        self.mouse.height = 32.0
        
        self.kitten = Kitten(x=0.0, y=0.0)
        self.kitten.width = 32.0
        self.kitten.height = 32.0

    def test_clamp_entities_inside_bounds(self) -> None:
        """Test that entities inside bounds are not clamped."""
        self.mouse.x = 100.0
        self.mouse.y = 100.0
        self.kitten.x = 200.0
        self.kitten.y = 200.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        self.assertEqual(self.mouse.x, 100.0)
        self.assertEqual(self.mouse.y, 100.0)
        self.assertEqual(self.kitten.x, 200.0)
        self.assertEqual(self.kitten.y, 200.0)

    def test_clamp_mouse_left_boundary(self) -> None:
        """Test clamping mouse to left boundary."""
        self.mouse.x = -10.0
        self.mouse.y = 100.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        self.assertEqual(self.mouse.x, 0.0)
        self.assertEqual(self.mouse.y, 100.0)

    def test_clamp_mouse_right_boundary(self) -> None:
        """Test clamping mouse to right boundary."""
        self.mouse.x = 800.0
        self.mouse.y = 100.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        # x should be clamped to (800 - 32) = 768
        self.assertEqual(self.mouse.x, 768.0)
        self.assertEqual(self.mouse.y, 100.0)

    def test_clamp_mouse_top_boundary(self) -> None:
        """Test clamping mouse to top boundary."""
        self.mouse.x = 100.0
        self.mouse.y = -10.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        self.assertEqual(self.mouse.x, 100.0)
        self.assertEqual(self.mouse.y, 0.0)

    def test_clamp_mouse_bottom_boundary(self) -> None:
        """Test clamping mouse to bottom boundary."""
        self.mouse.x = 100.0
        self.mouse.y = 600.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        # y should be clamped to (600 - 32) = 568
        self.assertEqual(self.mouse.x, 100.0)
        self.assertEqual(self.mouse.y, 568.0)

    def test_clamp_kitten_left_boundary(self) -> None:
        """Test clamping kitten to left boundary."""
        self.kitten.x = -10.0
        self.kitten.y = 100.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        self.assertEqual(self.kitten.x, 0.0)
        self.assertEqual(self.kitten.y, 100.0)

    def test_clamp_kitten_right_boundary(self) -> None:
        """Test clamping kitten to right boundary."""
        self.kitten.x = 800.0
        self.kitten.y = 100.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        self.assertEqual(self.kitten.x, 768.0)
        self.assertEqual(self.kitten.y, 100.0)

    def test_clamp_both_entities_corner(self) -> None:
        """Test clamping both entities at corner."""
        self.mouse.x = -10.0
        self.mouse.y = -10.0
        self.kitten.x = 800.0
        self.kitten.y = 600.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 800.0, 600.0)
        
        self.assertEqual(self.mouse.x, 0.0)
        self.assertEqual(self.mouse.y, 0.0)
        self.assertEqual(self.kitten.x, 768.0)
        self.assertEqual(self.kitten.y, 568.0)

    def test_check_catch_not_caught(self) -> None:
        """Test that catch is not detected when far apart."""
        self.mouse.x = 0.0
        self.mouse.y = 0.0
        self.kitten.x = 500.0
        self.kitten.y = 500.0
        
        is_caught = check_catch_condition(self.mouse, self.kitten, catch_range=50.0)
        
        self.assertFalse(is_caught)

    def test_check_catch_at_exact_distance(self) -> None:
        """Test catch at catch_range boundary."""
        self.mouse.x = 0.0
        self.mouse.y = 0.0
        # Center of mouse at (16, 16)
        # Distance to target should be catch_range
        # Place kitten so distance = ~100 from mouse center
        catch_range = 100.0
        self.kitten.x = 84.0  # Distance from (16,16) to (100,16) is 84
        self.kitten.y = 0.0
        
        is_caught = check_catch_condition(self.mouse, self.kitten, catch_range=catch_range)
        
        self.assertTrue(is_caught)

    def test_check_catch_within_range(self) -> None:
        """Test catch detection when within range."""
        self.mouse.x = 0.0
        self.mouse.y = 0.0
        # Center at (16, 16), kitten center at (50, 50) = distance ~48
        self.kitten.x = 34.0
        self.kitten.y = 34.0
        
        is_caught = check_catch_condition(self.mouse, self.kitten, catch_range=100.0)
        
        self.assertTrue(is_caught)

    def test_check_catch_just_outside_range(self) -> None:
        """Test no catch when just outside range."""
        self.mouse.x = 0.0
        self.mouse.y = 0.0
        # Place kitten far enough to be outside catch_range
        self.kitten.x = 200.0
        self.kitten.y = 200.0
        
        is_caught = check_catch_condition(self.mouse, self.kitten, catch_range=50.0)
        
        self.assertFalse(is_caught)

    def test_check_catch_at_same_position(self) -> None:
        """Test catch when entities are at same position."""
        self.mouse.x = 100.0
        self.mouse.y = 100.0
        self.kitten.x = 100.0
        self.kitten.y = 100.0
        
        is_caught = check_catch_condition(self.mouse, self.kitten, catch_range=50.0)
        
        self.assertTrue(is_caught)

    def test_check_catch_zero_range(self) -> None:
        """Test catch with very small catch_range."""
        self.mouse.x = 0.0
        self.mouse.y = 0.0
        # Center at (16, 16), kitten center at (16.5, 16)
        self.kitten.x = 0.5
        self.kitten.y = 0.0
        
        # With catch_range = 1.0, distance = 0.5, should be caught
        is_caught = check_catch_condition(self.mouse, self.kitten, catch_range=1.0)
        
        self.assertTrue(is_caught)

    def test_clamp_with_different_window_sizes(self) -> None:
        """Test clamping with non-standard window sizes."""
        self.mouse.x = -10.0
        self.mouse.y = -10.0
        self.kitten.x = 2560.0
        self.kitten.y = 1600.0
        
        clamp_entities_to_bounds(self.mouse, self.kitten, 2560.0, 1600.0)
        
        self.assertEqual(self.mouse.x, 0.0)
        self.assertEqual(self.mouse.y, 0.0)
        self.assertEqual(self.kitten.x, 2560.0 - 32.0)
        self.assertEqual(self.kitten.y, 1600.0 - 32.0)


if __name__ == "__main__":
    unittest.main()
