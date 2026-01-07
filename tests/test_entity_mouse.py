"""Tests for the Mouse entity class."""

import unittest

from pyglet_readme.config import CONFIG
from pyglet_readme.entities.base import EntityState
from pyglet_readme.entities.mouse import Mouse


class TestMouse(unittest.TestCase):
    """Test the Mouse entity class."""

    def test_mouse_creation(self) -> None:
        """Test creating a mouse entity with defaults."""
        mouse = Mouse()
        self.assertEqual(mouse.x, 0.0)
        self.assertEqual(mouse.y, 0.0)
        self.assertEqual(mouse.health, CONFIG.MAX_HEALTH)
        self.assertEqual(mouse.state, EntityState.IDLE)

    def test_mouse_custom_position(self) -> None:
        """Test creating mouse with custom position."""
        mouse = Mouse(x=100.0, y=200.0)
        self.assertEqual(mouse.x, 100.0)
        self.assertEqual(mouse.y, 200.0)

    def test_mouse_custom_health(self) -> None:
        """Test creating mouse with custom health."""
        mouse = Mouse(health=50.0)
        self.assertEqual(mouse.health, 50.0)

    def test_mouse_keyboard_input_up(self) -> None:
        """Test keyboard input for up movement."""
        mouse = Mouse()
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_from_keyboard(up=True, down=False, left=False, right=False)
        self.assertGreater(mouse.vy, 0)
        self.assertEqual(mouse.vx, 0.0)
        self.assertEqual(mouse.state, EntityState.MOVING)

    def test_mouse_keyboard_input_down(self) -> None:
        """Test keyboard input for down movement."""
        mouse = Mouse()
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_from_keyboard(up=False, down=True, left=False, right=False)
        self.assertLess(mouse.vy, 0)
        self.assertEqual(mouse.vx, 0.0)
        self.assertEqual(mouse.state, EntityState.MOVING)

    def test_mouse_keyboard_input_left(self) -> None:
        """Test keyboard input for left movement."""
        mouse = Mouse()
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_from_keyboard(up=False, down=False, left=True, right=False)
        self.assertLess(mouse.vx, 0)
        self.assertEqual(mouse.vy, 0.0)
        self.assertEqual(mouse.state, EntityState.MOVING)

    def test_mouse_keyboard_input_right(self) -> None:
        """Test keyboard input for right movement."""
        mouse = Mouse()
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_from_keyboard(up=False, down=False, left=False, right=True)
        self.assertGreater(mouse.vx, 0)
        self.assertEqual(mouse.vy, 0.0)
        self.assertEqual(mouse.state, EntityState.MOVING)

    def test_mouse_keyboard_input_diagonal(self) -> None:
        """Test keyboard input for diagonal movement."""
        mouse = Mouse()
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_from_keyboard(up=True, down=False, left=True, right=False)
        # Diagonal movement should apply diagonal factor (0.7071)
        self.assertGreater(mouse.vy, 0)
        self.assertLess(mouse.vx, 0)
        self.assertEqual(mouse.state, EntityState.MOVING)

    def test_mouse_keyboard_input_idle(self) -> None:
        """Test keyboard input with no keys pressed results in idle."""
        mouse = Mouse(vx=50.0, vy=50.0)
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_from_keyboard(up=False, down=False, left=False, right=False)
        self.assertEqual(mouse.vx, 0.0)
        self.assertEqual(mouse.vy, 0.0)
        self.assertEqual(mouse.state, EntityState.IDLE)

    def test_mouse_click_velocity(self) -> None:
        """Test velocity calculation from click target."""
        mouse = Mouse(x=0.0, y=0.0)
        mouse.width = 32.0
        mouse.height = 32.0
        # Click at (100, 100), mouse center at (16, 16)
        mouse.update_from_click(target_x=100.0, target_y=100.0)
        self.assertGreater(mouse.vx, 0)
        self.assertGreater(mouse.vy, 0)
        self.assertEqual(mouse.state, EntityState.MOVING)

    def test_mouse_click_velocity_zero_distance(self) -> None:
        """Test click at current position results in zero velocity."""
        mouse = Mouse(x=0.0, y=0.0)
        mouse.width = 32.0
        mouse.height = 32.0
        # Click at mouse center
        mouse.update_from_click(target_x=16.0, target_y=16.0)
        self.assertEqual(mouse.vx, 0.0)
        self.assertEqual(mouse.vy, 0.0)
        self.assertEqual(mouse.state, EntityState.IDLE)

    def test_mouse_apply_health_change_damage(self) -> None:
        """Test applying health damage."""
        mouse = Mouse(health=100.0)
        mouse.apply_health_change(-25.0)
        self.assertEqual(mouse.health, 75.0)

    def test_mouse_apply_health_change_heal(self) -> None:
        """Test applying health healing."""
        mouse = Mouse(health=50.0)
        mouse.apply_health_change(25.0)
        self.assertEqual(mouse.health, 75.0)

    def test_mouse_apply_health_change_clamps_max(self) -> None:
        """Test that health is clamped to max."""
        mouse = Mouse(health=90.0)
        mouse.apply_health_change(20.0)
        self.assertEqual(mouse.health, CONFIG.MAX_HEALTH)

    def test_mouse_apply_health_change_clamps_min(self) -> None:
        """Test that health is clamped to zero."""
        mouse = Mouse(health=10.0)
        mouse.apply_health_change(-20.0)
        self.assertEqual(mouse.health, 0.0)

    def test_mouse_is_alive_true(self) -> None:
        """Test that mouse is alive when health > 0."""
        mouse = Mouse(health=50.0)
        self.assertTrue(mouse.is_alive())

    def test_mouse_is_alive_false(self) -> None:
        """Test that mouse is dead when health == 0."""
        mouse = Mouse(health=0.0)
        self.assertFalse(mouse.is_alive())

    def test_mouse_is_alive_true_at_max(self) -> None:
        """Test that mouse is alive at max health."""
        mouse = Mouse(health=CONFIG.MAX_HEALTH)
        self.assertTrue(mouse.is_alive())

    def test_mouse_update_position(self) -> None:
        """Test updating mouse position based on velocity."""
        mouse = Mouse(x=0.0, y=0.0, vx=100.0, vy=50.0)
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_position(dt=1.0)
        self.assertEqual(mouse.x, 100.0)
        self.assertEqual(mouse.y, 50.0)

    def test_mouse_update_position_with_delta_time(self) -> None:
        """Test position update with fractional delta time."""
        mouse = Mouse(x=0.0, y=0.0, vx=100.0, vy=50.0)
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.update_position(dt=0.5)
        self.assertEqual(mouse.x, 50.0)
        self.assertEqual(mouse.y, 25.0)

    def test_mouse_inherited_clamp_to_bounds(self) -> None:
        """Test that mouse inherits clamp_to_bounds from Entity."""
        mouse = Mouse(x=-10.0, y=-10.0)
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(mouse.x, 0.0)
        self.assertEqual(mouse.y, 0.0)

    def test_mouse_reset(self) -> None:
        """Test resetting mouse to initial state."""
        mouse = Mouse(x=100.0, y=200.0, vx=50.0, vy=50.0, health=25.0)
        mouse.width = 32.0
        mouse.height = 32.0
        mouse.state = EntityState.MOVING
        
        mouse.reset()
        
        self.assertEqual(mouse.x, 0.0)
        self.assertEqual(mouse.y, 0.0)
        self.assertEqual(mouse.vx, 0.0)
        self.assertEqual(mouse.vy, 0.0)
        self.assertEqual(mouse.health, CONFIG.MAX_HEALTH)
        self.assertEqual(mouse.state, EntityState.IDLE)

    def test_mouse_reset_damaged(self) -> None:
        """Test that reset restores health even if severely damaged."""
        mouse = Mouse(x=500.0, y=500.0, health=5.0)
        mouse.width = 32.0
        mouse.height = 32.0
        
        mouse.reset()
        
        self.assertEqual(mouse.health, CONFIG.MAX_HEALTH)
        self.assertEqual(mouse.x, 0.0)
        self.assertEqual(mouse.y, 0.0)

    def test_mouse_reset_multiple_times(self) -> None:
        """Test that mouse can be reset multiple times."""
        mouse = Mouse()
        mouse.width = 32.0
        mouse.height = 32.0
        
        # First state change and reset
        mouse.x = 100.0
        mouse.health = 50.0
        mouse.reset()
        self.assertEqual(mouse.x, 0.0)
        self.assertEqual(mouse.health, CONFIG.MAX_HEALTH)
        
        # Second state change and reset
        mouse.x = 200.0
        mouse.health = 25.0
        mouse.reset()
        self.assertEqual(mouse.x, 0.0)
        self.assertEqual(mouse.health, CONFIG.MAX_HEALTH)


if __name__ == "__main__":
    unittest.main()
