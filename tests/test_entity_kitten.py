"""Tests for the Kitten entity class."""

import unittest

from chaser_game.config import CONFIG
from chaser_game.entities.base import EntityState
from chaser_game.entities.kitten import Kitten


class TestKitten(unittest.TestCase):
    """Test the Kitten entity class."""

    def test_kitten_creation(self) -> None:
        """Test creating a kitten entity with defaults."""
        kitten = Kitten()
        self.assertEqual(kitten.x, 0.0)
        self.assertEqual(kitten.y, 0.0)
        self.assertEqual(kitten.stamina, CONFIG.MAX_STAMINA)
        self.assertFalse(kitten.is_moving)
        self.assertEqual(kitten.state, EntityState.IDLE)

    def test_kitten_custom_position(self) -> None:
        """Test creating kitten with custom position."""
        kitten = Kitten(x=100.0, y=200.0)
        self.assertEqual(kitten.x, 100.0)
        self.assertEqual(kitten.y, 200.0)

    def test_kitten_custom_stamina(self) -> None:
        """Test creating kitten with custom stamina."""
        kitten = Kitten(stamina=50.0)
        self.assertEqual(kitten.stamina, 50.0)

    def test_kitten_speed_calculation(self) -> None:
        """Test that kitten speed is slower than base speed."""
        kitten = Kitten()
        base_speed = CONFIG.WINDOW_WIDTH / CONFIG.WINDOW_TRAVERSAL_TIME
        expected_kitten_speed = base_speed / CONFIG.KITTEN_SPEED_FACTOR
        self.assertAlmostEqual(kitten.speed, expected_kitten_speed, places=2)

    def test_kitten_chase_target_moving(self) -> None:
        """Test kitten chase velocity when target is far."""
        kitten = Kitten(x=0.0, y=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        # Target is far away (100, 100 from center at 16, 16)
        kitten.update_chase_target(target_x=100.0, target_y=100.0)
        self.assertGreater(kitten.vx, 0)
        self.assertGreater(kitten.vy, 0)
        self.assertTrue(kitten.is_moving)
        self.assertEqual(kitten.state, EntityState.CHASING)

    def test_kitten_chase_target_stopped_near(self) -> None:
        """Test kitten stops when very close to target."""
        kitten = Kitten(x=0.0, y=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        # Target is within distance threshold (center at 16, 16)
        kitten.update_chase_target(target_x=17.0, target_y=16.0)
        self.assertEqual(kitten.vx, 0.0)
        self.assertEqual(kitten.vy, 0.0)
        self.assertFalse(kitten.is_moving)
        self.assertEqual(kitten.state, EntityState.IDLE)

    def test_kitten_chase_target_exact_position(self) -> None:
        """Test kitten stops when at exact target position."""
        kitten = Kitten(x=0.0, y=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        # Target is at center
        kitten.update_chase_target(target_x=16.0, target_y=16.0)
        self.assertEqual(kitten.vx, 0.0)
        self.assertEqual(kitten.vy, 0.0)

    def test_kitten_apply_stamina_change_gain(self) -> None:
        """Test gaining stamina."""
        kitten = Kitten(stamina=50.0)
        kitten.apply_stamina_change(25.0)
        self.assertEqual(kitten.stamina, 75.0)

    def test_kitten_apply_stamina_change_drain(self) -> None:
        """Test draining stamina."""
        kitten = Kitten(stamina=100.0)
        kitten.apply_stamina_change(-30.0)
        self.assertEqual(kitten.stamina, 70.0)

    def test_kitten_apply_stamina_change_clamps_max(self) -> None:
        """Test that stamina is clamped to max."""
        kitten = Kitten(stamina=90.0)
        kitten.apply_stamina_change(20.0)
        self.assertEqual(kitten.stamina, CONFIG.MAX_STAMINA)

    def test_kitten_apply_stamina_change_clamps_min(self) -> None:
        """Test that stamina is clamped to zero."""
        kitten = Kitten(stamina=10.0)
        kitten.apply_stamina_change(-20.0)
        self.assertEqual(kitten.stamina, 0.0)

    def test_kitten_has_stamina_true(self) -> None:
        """Test that kitten has stamina when stamina > 0."""
        kitten = Kitten(stamina=50.0)
        self.assertTrue(kitten.has_stamina())

    def test_kitten_has_stamina_false(self) -> None:
        """Test that kitten has no stamina when stamina == 0."""
        kitten = Kitten(stamina=0.0)
        self.assertFalse(kitten.has_stamina())

    def test_kitten_has_stamina_true_at_max(self) -> None:
        """Test that kitten has stamina at max."""
        kitten = Kitten(stamina=CONFIG.MAX_STAMINA)
        self.assertTrue(kitten.has_stamina())

    def test_kitten_get_distance_to_target(self) -> None:
        """Test distance calculation to target."""
        kitten = Kitten(x=0.0, y=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        # Center at (16, 16), target at (100, 100)
        # Distance = sqrt((100-16)^2 + (100-16)^2) = sqrt(2 * 84^2) ≈ 118.79
        distance = kitten.get_distance_to_target(target_x=100.0, target_y=100.0)
        self.assertGreater(distance, 100.0)
        self.assertLess(distance, 150.0)

    def test_kitten_get_distance_to_target_at_position(self) -> None:
        """Test distance to target at exact position."""
        kitten = Kitten(x=0.0, y=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        # Center at (16, 16), target at same point
        distance = kitten.get_distance_to_target(target_x=16.0, target_y=16.0)
        self.assertEqual(distance, 0.0)

    def test_kitten_update_position(self) -> None:
        """Test updating kitten position based on velocity."""
        kitten = Kitten(x=0.0, y=0.0, vx=100.0, vy=50.0)
        kitten.width = 32.0
        kitten.height = 32.0
        kitten.update_position(dt=1.0)
        self.assertGreater(kitten.x, 0.0)
        self.assertGreater(kitten.y, 0.0)

    def test_kitten_update_position_with_delta_time(self) -> None:
        """Test position update with fractional delta time."""
        kitten = Kitten(x=0.0, y=0.0, vx=100.0, vy=50.0)
        kitten.width = 32.0
        kitten.height = 32.0
        kitten.update_position(dt=0.5)
        # Should move less than full second
        self.assertGreater(kitten.x, 0.0)
        self.assertLess(kitten.x, 100.0)

    def test_kitten_update_position_zero_velocity(self) -> None:
        """Test that position doesn't change with zero velocity."""
        kitten = Kitten(x=50.0, y=50.0, vx=0.0, vy=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        kitten.update_position(dt=1.0)
        self.assertEqual(kitten.x, 50.0)
        self.assertEqual(kitten.y, 50.0)

    def test_kitten_inherited_clamp_to_bounds(self) -> None:
        """Test that kitten inherits clamp_to_bounds from Entity."""
        kitten = Kitten(x=-10.0, y=-10.0)
        kitten.width = 32.0
        kitten.height = 32.0
        kitten.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(kitten.x, 0.0)
        self.assertEqual(kitten.y, 0.0)

    def test_kitten_inherited_set_velocity(self) -> None:
        """Test that kitten inherits set_velocity from Entity."""
        kitten = Kitten()
        kitten.set_velocity(vx=75.0, vy=-50.0)
        self.assertEqual(kitten.vx, 75.0)
        self.assertEqual(kitten.vy, -50.0)

    def test_kitten_inherited_stop(self) -> None:
        """Test that kitten inherits stop from Entity."""
        kitten = Kitten(vx=100.0, vy=50.0)
        kitten.stop()
        self.assertEqual(kitten.vx, 0.0)
        self.assertEqual(kitten.vy, 0.0)

    def test_kitten_reset(self) -> None:
        """Test resetting kitten to initial state."""
        kitten = Kitten(x=100.0, y=200.0, vx=50.0, vy=50.0, stamina=25.0)
        kitten.width = 32.0
        kitten.height = 32.0
        kitten.is_moving = True
        kitten.state = EntityState.CHASING
        
        kitten.reset(window_width=800.0, window_height=600.0)
        
        expected_x = 800.0 * CONFIG.KITTEN_START_X_RATIO
        expected_y = 600.0 * CONFIG.KITTEN_START_Y_RATIO
        self.assertEqual(kitten.x, expected_x)
        self.assertEqual(kitten.y, expected_y)
        self.assertEqual(kitten.vx, 0.0)
        self.assertEqual(kitten.vy, 0.0)
        self.assertEqual(kitten.stamina, CONFIG.MAX_STAMINA)
        self.assertFalse(kitten.is_moving)
        self.assertEqual(kitten.state, EntityState.IDLE)

    def test_kitten_reset_exhausted(self) -> None:
        """Test that reset restores stamina even if exhausted."""
        kitten = Kitten(x=500.0, y=500.0, stamina=0.0)
        kitten.width = 32.0
        kitten.height = 32.0
        
        kitten.reset(window_width=800.0, window_height=600.0)
        
        self.assertEqual(kitten.stamina, CONFIG.MAX_STAMINA)
        expected_x = 800.0 * CONFIG.KITTEN_START_X_RATIO
        self.assertEqual(kitten.x, expected_x)

    def test_kitten_reset_multiple_times(self) -> None:
        """Test that kitten can be reset multiple times."""
        kitten = Kitten()
        kitten.width = 32.0
        kitten.height = 32.0
        
        # First state change and reset
        kitten.x = 100.0
        kitten.stamina = 50.0
        kitten.reset(window_width=800.0, window_height=600.0)
        expected_x = 800.0 * CONFIG.KITTEN_START_X_RATIO
        self.assertEqual(kitten.x, expected_x)
        self.assertEqual(kitten.stamina, CONFIG.MAX_STAMINA)
        
        # Second state change and reset
        kitten.x = 200.0
        kitten.stamina = 25.0
        kitten.reset(window_width=800.0, window_height=600.0)
        self.assertEqual(kitten.x, expected_x)
        self.assertEqual(kitten.stamina, CONFIG.MAX_STAMINA)


if __name__ == "__main__":
    unittest.main()
