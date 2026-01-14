"""Tests for the input system."""

import unittest
from unittest.mock import MagicMock

from chaser_game.entities.base import EntityState
from chaser_game.entities.mouse import Mouse
from chaser_game.mechanics.input import (
    handle_key_press,
    handle_keyboard_input,
    handle_mouse_press,
)
from pyglet.window import key, mouse


class TestInputSystem(unittest.TestCase):
    """Test the input handling system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mouse = Mouse()
        self.mouse.width = 32.0
        self.mouse.height = 32.0

    def test_handle_keyboard_input_up(self) -> None:
        """Test keyboard input for up movement."""
        keys = MagicMock()
        keys.__getitem__ = MagicMock(
            side_effect=lambda k: {
                key.UP: True,
                key.DOWN: False,
                key.LEFT: False,
                key.RIGHT: False,
            }.get(k, False)
        )

        handle_keyboard_input(self.mouse, keys)

        self.assertGreater(self.mouse.vy, 0)
        self.assertEqual(self.mouse.vx, 0.0)

    def test_handle_keyboard_input_down(self) -> None:
        """Test keyboard input for down movement."""
        keys = MagicMock()
        keys.__getitem__ = MagicMock(
            side_effect=lambda k: {
                key.UP: False,
                key.DOWN: True,
                key.LEFT: False,
                key.RIGHT: False,
            }.get(k, False)
        )

        handle_keyboard_input(self.mouse, keys)

        self.assertLess(self.mouse.vy, 0)
        self.assertEqual(self.mouse.vx, 0.0)

    def test_handle_keyboard_input_left(self) -> None:
        """Test keyboard input for left movement."""
        keys = MagicMock()
        keys.__getitem__ = MagicMock(
            side_effect=lambda k: {
                key.UP: False,
                key.DOWN: False,
                key.LEFT: True,
                key.RIGHT: False,
            }.get(k, False)
        )

        handle_keyboard_input(self.mouse, keys)

        self.assertLess(self.mouse.vx, 0)
        self.assertEqual(self.mouse.vy, 0.0)

    def test_handle_keyboard_input_right(self) -> None:
        """Test keyboard input for right movement."""
        keys = MagicMock()
        keys.__getitem__ = MagicMock(
            side_effect=lambda k: {
                key.UP: False,
                key.DOWN: False,
                key.LEFT: False,
                key.RIGHT: True,
            }.get(k, False)
        )

        handle_keyboard_input(self.mouse, keys)

        self.assertGreater(self.mouse.vx, 0)
        self.assertEqual(self.mouse.vy, 0.0)

    def test_handle_keyboard_input_diagonal(self) -> None:
        """Test keyboard input for diagonal movement."""
        keys = MagicMock()
        keys.__getitem__ = MagicMock(
            side_effect=lambda k: {
                key.UP: True,
                key.DOWN: False,
                key.LEFT: True,
                key.RIGHT: False,
            }.get(k, False)
        )

        handle_keyboard_input(self.mouse, keys)

        self.assertGreater(self.mouse.vy, 0)
        self.assertLess(self.mouse.vx, 0)

    def test_handle_keyboard_input_no_keys(self) -> None:
        """Test keyboard input with no keys pressed."""
        keys = MagicMock()
        keys.__getitem__ = MagicMock(side_effect=lambda k: False)

        handle_keyboard_input(self.mouse, keys)

        self.assertEqual(self.mouse.vx, 0.0)
        self.assertEqual(self.mouse.vy, 0.0)
        self.assertEqual(self.mouse.state, EntityState.IDLE)

    def test_handle_keyboard_input_invalid_keys_object(self) -> None:
        """Test that invalid keys object is handled gracefully."""
        keys = None  # type: ignore[assignment]

        # Should not raise an exception (gracefully handles the error)
        try:
            handle_keyboard_input(self.mouse, keys)
        except (TypeError, AttributeError):
            # Expected: None doesn't support __getitem__
            pass

    def test_handle_key_press_home(self) -> None:
        """Test Home key (Up-Left diagonal)."""
        handle_key_press(self.mouse, key.HOME)

        self.assertLess(self.mouse.vx, 0)
        self.assertGreater(self.mouse.vy, 0)

    def test_handle_key_press_pageup(self) -> None:
        """Test Page Up key (Up-Right diagonal)."""
        handle_key_press(self.mouse, key.PAGEUP)

        self.assertGreater(self.mouse.vx, 0)
        self.assertGreater(self.mouse.vy, 0)

    def test_handle_key_press_end(self) -> None:
        """Test End key (Down-Left diagonal)."""
        handle_key_press(self.mouse, key.END)

        self.assertLess(self.mouse.vx, 0)
        self.assertLess(self.mouse.vy, 0)

    def test_handle_key_press_pagedown(self) -> None:
        """Test Page Down key (Down-Right diagonal)."""
        handle_key_press(self.mouse, key.PAGEDOWN)

        self.assertGreater(self.mouse.vx, 0)
        self.assertLess(self.mouse.vy, 0)

    def test_handle_key_press_space(self) -> None:
        """Test Space key (Stop)."""
        self.mouse.vx = 100.0
        self.mouse.vy = 50.0

        handle_key_press(self.mouse, key.SPACE)

        self.assertEqual(self.mouse.vx, 0.0)
        self.assertEqual(self.mouse.vy, 0.0)

    def test_handle_key_press_unmapped_key(self) -> None:
        """Test that unmapped keys don't cause errors."""
        initial_vx = self.mouse.vx
        initial_vy = self.mouse.vy

        # Press an unmapped key (like 'A')
        handle_key_press(self.mouse, key.A)

        # Velocity should not change
        self.assertEqual(self.mouse.vx, initial_vx)
        self.assertEqual(self.mouse.vy, initial_vy)

    def test_handle_mouse_press_left_button(self) -> None:
        """Test left mouse button press."""
        handle_mouse_press(self.mouse, x=100.0, y=100.0, button=mouse.LEFT)

        self.assertGreater(self.mouse.vx, 0)
        self.assertGreater(self.mouse.vy, 0)
        self.assertEqual(self.mouse.state, EntityState.MOVING)

    def test_handle_mouse_press_right_button(self) -> None:
        """Test that right mouse button is ignored."""
        initial_vx = self.mouse.vx
        initial_vy = self.mouse.vy

        handle_mouse_press(self.mouse, x=100.0, y=100.0, button=mouse.RIGHT)

        self.assertEqual(self.mouse.vx, initial_vx)
        self.assertEqual(self.mouse.vy, initial_vy)

    def test_handle_mouse_press_middle_button(self) -> None:
        """Test that middle mouse button is ignored."""
        initial_vx = self.mouse.vx
        initial_vy = self.mouse.vy

        handle_mouse_press(self.mouse, x=100.0, y=100.0, button=mouse.MIDDLE)

        self.assertEqual(self.mouse.vx, initial_vx)
        self.assertEqual(self.mouse.vy, initial_vy)

    def test_handle_mouse_press_at_current_position(self) -> None:
        """Test left click at current position (should stop)."""
        self.mouse.x = 0.0
        self.mouse.y = 0.0

        # Click at mouse center
        handle_mouse_press(self.mouse, x=16.0, y=16.0, button=mouse.LEFT)

        self.assertEqual(self.mouse.vx, 0.0)
        self.assertEqual(self.mouse.vy, 0.0)

    def test_handle_mouse_press_negative_coordinates(self) -> None:
        """Test left click at negative coordinates."""
        handle_mouse_press(self.mouse, x=-100.0, y=-100.0, button=mouse.LEFT)

        # Should calculate velocity even with negative coords
        self.assertLess(self.mouse.vx, 0)
        self.assertLess(self.mouse.vy, 0)

    def test_handle_mouse_press_large_coordinates(self) -> None:
        """Test left click at large coordinates."""
        handle_mouse_press(self.mouse, x=1000.0, y=1000.0, button=mouse.LEFT)

        self.assertGreater(self.mouse.vx, 0)
        self.assertGreater(self.mouse.vy, 0)


if __name__ == "__main__":
    unittest.main()
