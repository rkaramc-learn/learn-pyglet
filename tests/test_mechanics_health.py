"""Tests for the mechanics.health module."""

import unittest

from chaser_game.config import CONFIG
from chaser_game.mechanics.health import update_health_stamina


class MockEntity:
    """Mock entity for testing health/stamina updates."""

    def __init__(
        self,
        center_x: float = 0.0,
        center_y: float = 0.0,
        width: float = 32.0,
        height: float = 32.0,
        health: float = CONFIG.MAX_HEALTH,
        stamina: float = CONFIG.MAX_STAMINA,
    ) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.health = health
        self.stamina = stamina


class TestUpdateHealthStamina(unittest.TestCase):
    """Test the update_health_stamina function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mouse = MockEntity(center_x=0.0, center_y=0.0)
        self.kitten = MockEntity(center_x=0.0, center_y=0.0)

    def test_no_damage_when_far_apart(self) -> None:
        """Test no health transfer when entities are far apart."""
        self.kitten.center_x = 500.0
        self.kitten.center_y = 500.0
        initial_health = self.mouse.health

        update_health_stamina(self.mouse, self.kitten, catch_range=50.0, dt=1.0)

        # Health should not change (distance > catch_range)
        self.assertEqual(self.mouse.health, initial_health)

    def test_passive_stamina_drain(self) -> None:
        """Test that stamina drains passively even when far away."""
        self.kitten.center_x = 500.0
        self.kitten.center_y = 500.0
        initial_stamina = self.kitten.stamina

        update_health_stamina(self.mouse, self.kitten, catch_range=50.0, dt=1.0)

        # Stamina should drain passively
        expected_drain = CONFIG.PASSIVE_STAMINA_DRAIN * 1.0
        self.assertAlmostEqual(self.kitten.stamina, initial_stamina - expected_drain, places=1)

    def test_health_transfer_at_zero_distance(self) -> None:
        """Test maximum health transfer when at same position."""
        initial_health = self.mouse.health

        update_health_stamina(self.mouse, self.kitten, catch_range=100.0, dt=1.0)

        # Mouse loses health
        self.assertLess(self.mouse.health, initial_health)
        # Kitten stamina is clamped at max (transfer exceeds passive drain)
        self.assertLessEqual(self.kitten.stamina, CONFIG.MAX_STAMINA)

    def test_health_transfer_scales_with_distance(self) -> None:
        """Test that health transfer scales with distance."""
        # Place kitten at half catch range
        catch_range = 100.0
        self.kitten.center_x = catch_range / 2

        initial_health = self.mouse.health

        update_health_stamina(self.mouse, self.kitten, catch_range=catch_range, dt=1.0)

        # At proximity_factor = 0.5, transfer = BASE_DRAIN_RATE * 0.5
        expected_loss = CONFIG.BASE_DRAIN_RATE * 0.5 * 1.0
        self.assertAlmostEqual(self.mouse.health, initial_health - expected_loss, places=1)

    def test_health_clamped_at_zero(self) -> None:
        """Test that health doesn't go below zero."""
        self.mouse.health = 1.0

        # Apply massive damage
        update_health_stamina(self.mouse, self.kitten, catch_range=100.0, dt=100.0)

        self.assertGreaterEqual(self.mouse.health, 0.0)

    def test_stamina_clamped_at_max(self) -> None:
        """Test that stamina doesn't exceed maximum."""
        self.kitten.stamina = CONFIG.MAX_STAMINA - 1.0

        # Apply massive stamina gain
        update_health_stamina(self.mouse, self.kitten, catch_range=100.0, dt=100.0)

        self.assertLessEqual(self.kitten.stamina, CONFIG.MAX_STAMINA)

    def test_framerate_independence(self) -> None:
        """Test that health transfer scales with delta time."""
        mouse1 = MockEntity()
        kitten1 = MockEntity()
        mouse2 = MockEntity()
        kitten2 = MockEntity()

        # Test with dt = 0.5
        update_health_stamina(mouse1, kitten1, catch_range=100.0, dt=0.5)
        loss1 = CONFIG.MAX_HEALTH - mouse1.health

        # Test with dt = 1.0
        update_health_stamina(mouse2, kitten2, catch_range=100.0, dt=1.0)
        loss2 = CONFIG.MAX_HEALTH - mouse2.health

        # Loss with dt=1.0 should be ~2x loss with dt=0.5
        self.assertAlmostEqual(loss2, loss1 * 2.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
