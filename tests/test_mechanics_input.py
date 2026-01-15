"""Tests for the mechanics.input module."""

import unittest

from chaser_game.mechanics.input import (
    handle_key_press,
    handle_keyboard_input,
    handle_mouse_press,
)
from pyglet.window import key, mouse


class MockEntity:
    """Mock entity for testing input handling."""

    def __init__(self) -> None:
        self.keyboard_calls: list[tuple[bool, bool, bool, bool]] = []
        self.velocity_targets: list[tuple[float, float]] = []
        self.stopped = False

    def update_from_keyboard(self, up: bool, down: bool, left: bool, right: bool) -> None:
        """Record keyboard update call."""
        self.keyboard_calls.append((up, down, left, right))

    def set_velocity_to_target(self, target_x: float, target_y: float) -> None:
        """Record velocity target call."""
        self.velocity_targets.append((target_x, target_y))

    def stop(self) -> None:
        """Record stop call."""
        self.stopped = True


class MockKeyHandler:
    """Mock pyglet KeyStateHandler."""

    def __init__(self, keys: dict[int, bool] | None = None) -> None:
        self._keys = keys or {}

    def __getitem__(self, key_code: int) -> bool:
        return self._keys.get(key_code, False)


class TestHandleKeyboardInput(unittest.TestCase):
    """Test the handle_keyboard_input function."""

    def test_all_keys_released(self) -> None:
        """Test when no keys are pressed."""
        entity = MockEntity()
        keys = MockKeyHandler({})

        handle_keyboard_input(entity, keys)

        self.assertEqual(len(entity.keyboard_calls), 1)
        self.assertEqual(entity.keyboard_calls[0], (False, False, False, False))

    def test_up_key_pressed(self) -> None:
        """Test when up key is pressed."""
        entity = MockEntity()
        keys = MockKeyHandler({key.UP: True})

        handle_keyboard_input(entity, keys)

        self.assertEqual(entity.keyboard_calls[0], (True, False, False, False))

    def test_diagonal_keys(self) -> None:
        """Test when multiple keys are pressed for diagonal movement."""
        entity = MockEntity()
        keys = MockKeyHandler({key.UP: True, key.RIGHT: True})

        handle_keyboard_input(entity, keys)

        self.assertEqual(entity.keyboard_calls[0], (True, False, False, True))

    def test_handles_invalid_keys_gracefully(self) -> None:
        """Test that invalid key handlers don't crash."""
        entity = MockEntity()

        # Pass None or invalid handler
        handle_keyboard_input(entity, None)  # Should not raise

        # No calls should be made
        self.assertEqual(len(entity.keyboard_calls), 0)


class TestHandleKeyPress(unittest.TestCase):
    """Test the handle_key_press function."""

    def test_home_key_up_left(self) -> None:
        """Test HOME key for up-left diagonal."""
        entity = MockEntity()

        handle_key_press(entity, key.HOME)

        self.assertEqual(entity.keyboard_calls[0], (True, False, True, False))

    def test_pageup_key_up_right(self) -> None:
        """Test PAGEUP key for up-right diagonal."""
        entity = MockEntity()

        handle_key_press(entity, key.PAGEUP)

        self.assertEqual(entity.keyboard_calls[0], (True, False, False, True))

    def test_end_key_down_left(self) -> None:
        """Test END key for down-left diagonal."""
        entity = MockEntity()

        handle_key_press(entity, key.END)

        self.assertEqual(entity.keyboard_calls[0], (False, True, True, False))

    def test_pagedown_key_down_right(self) -> None:
        """Test PAGEDOWN key for down-right diagonal."""
        entity = MockEntity()

        handle_key_press(entity, key.PAGEDOWN)

        self.assertEqual(entity.keyboard_calls[0], (False, True, False, True))

    def test_space_key_stops_entity(self) -> None:
        """Test SPACE key stops the entity."""
        entity = MockEntity()

        handle_key_press(entity, key.SPACE)

        self.assertTrue(entity.stopped)

    def test_unhandled_key_no_action(self) -> None:
        """Test unhandled key does nothing."""
        entity = MockEntity()

        handle_key_press(entity, key.A)  # Not handled

        self.assertEqual(len(entity.keyboard_calls), 0)
        self.assertFalse(entity.stopped)


class TestHandleMousePress(unittest.TestCase):
    """Test the handle_mouse_press function."""

    def test_left_click_sets_target(self) -> None:
        """Test left click sets velocity target."""
        entity = MockEntity()

        handle_mouse_press(entity, 100.0, 200.0, mouse.LEFT)

        self.assertEqual(len(entity.velocity_targets), 1)
        self.assertEqual(entity.velocity_targets[0], (100.0, 200.0))

    def test_right_click_no_action(self) -> None:
        """Test right click does nothing."""
        entity = MockEntity()

        handle_mouse_press(entity, 100.0, 200.0, mouse.RIGHT)

        self.assertEqual(len(entity.velocity_targets), 0)

    def test_middle_click_no_action(self) -> None:
        """Test middle click does nothing."""
        entity = MockEntity()

        handle_mouse_press(entity, 100.0, 200.0, mouse.MIDDLE)

        self.assertEqual(len(entity.velocity_targets), 0)


if __name__ == "__main__":
    unittest.main()
