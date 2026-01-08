"""Tests for the health system."""

import unittest

from chaser_game.config import CONFIG
from chaser_game.entities.kitten import Kitten
from chaser_game.entities.mouse import Mouse
from chaser_game.systems.health import update_health_stamina


class TestHealthSystem(unittest.TestCase):
    """Test the health and stamina update system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mouse = Mouse(x=0.0, y=0.0, health=CONFIG.MAX_HEALTH)
        self.mouse.width = 32.0
        self.mouse.height = 32.0
        
        self.kitten = Kitten(x=0.0, y=0.0, stamina=CONFIG.MAX_STAMINA)
        self.kitten.width = 32.0
        self.kitten.height = 32.0

    def test_health_update_no_damage_far_away(self) -> None:
        """Test no health transfer when entities are far apart (but stamina drains passively)."""
        # Place kitten far away
        self.kitten.x = 500.0
        self.kitten.y = 500.0
        
        initial_health = self.mouse.health
        
        # Catch range is small, distance is large
        update_health_stamina(self.mouse, self.kitten, catch_range=50.0, dt=1.0)
        
        # Health should not change (no proximity)
        self.assertEqual(self.mouse.health, initial_health)
        # Stamina should drain passively
        self.assertLess(self.kitten.stamina, CONFIG.MAX_STAMINA)

    def test_health_transfer_at_max_proximity(self) -> None:
        """Test maximum health transfer when at zero distance."""
        # Place kitten at exact same position (distance = 0)
        self.kitten.x = self.mouse.x
        self.kitten.y = self.mouse.y
        
        catch_range = 100.0
        initial_health = self.mouse.health
        initial_stamina = self.kitten.stamina
        
        update_health_stamina(self.mouse, self.kitten, catch_range=catch_range, dt=1.0)
        
        # At proximity_factor = 1.0, transfer = BASE_DRAIN_RATE * 1.0 * dt
        expected_transfer = CONFIG.BASE_DRAIN_RATE * 1.0
        
        self.assertLess(self.mouse.health, initial_health)
        self.assertGreater(self.kitten.stamina, initial_stamina - expected_transfer)

    def test_health_transfer_at_partial_proximity(self) -> None:
        """Test health transfer scales with distance."""
        # Place kitten at catch_range / 2
        catch_range = 100.0
        self.kitten.x = self.mouse.x + (catch_range / 2)
        self.kitten.y = self.mouse.y
        
        initial_health = self.mouse.health
        
        update_health_stamina(self.mouse, self.kitten, catch_range=catch_range, dt=1.0)
        
        # At proximity_factor = 0.5, transfer = BASE_DRAIN_RATE * 0.5 * dt
        expected_health_loss = CONFIG.BASE_DRAIN_RATE * 0.5 * 1.0
        expected_health = initial_health - expected_health_loss
        
        self.assertAlmostEqual(self.mouse.health, expected_health, places=1)

    def test_passive_stamina_drain(self) -> None:
        """Test that stamina drains passively even when far away."""
        # Place kitten far away
        self.kitten.x = 500.0
        self.kitten.y = 500.0
        
        initial_stamina = self.kitten.stamina
        dt = 1.0
        
        update_health_stamina(self.mouse, self.kitten, catch_range=50.0, dt=dt)
        
        # Passive drain = PASSIVE_STAMINA_DRAIN * dt
        expected_stamina = initial_stamina - (CONFIG.PASSIVE_STAMINA_DRAIN * dt)
        
        self.assertAlmostEqual(self.kitten.stamina, expected_stamina, places=1)

    def test_health_clamped_at_zero(self) -> None:
        """Test that health doesn't go below zero."""
        # Place kitten on top of mouse
        self.kitten.x = self.mouse.x
        self.kitten.y = self.mouse.y
        
        # Set mouse health to very low
        self.mouse.health = 5.0
        
        # Apply large damage with large dt
        update_health_stamina(self.mouse, self.kitten, catch_range=100.0, dt=10.0)
        
        self.assertGreaterEqual(self.mouse.health, 0.0)

    def test_stamina_clamped_at_max(self) -> None:
        """Test that stamina doesn't exceed maximum."""
        # Place kitten on top of mouse
        self.kitten.x = self.mouse.x
        self.kitten.y = self.mouse.y
        
        # Set kitten stamina close to max
        self.kitten.stamina = CONFIG.MAX_STAMINA - 5.0
        
        # Apply large transfer with large dt
        update_health_stamina(self.mouse, self.kitten, catch_range=100.0, dt=10.0)
        
        self.assertLessEqual(self.kitten.stamina, CONFIG.MAX_STAMINA)

    def test_multiple_updates(self) -> None:
        """Test multiple sequential updates."""
        catch_range = 100.0
        self.kitten.x = self.mouse.x
        self.kitten.y = self.mouse.y
        
        # First update
        update_health_stamina(self.mouse, self.kitten, catch_range=catch_range, dt=0.1)
        health_after_first = self.mouse.health
        
        # Second update
        update_health_stamina(self.mouse, self.kitten, catch_range=catch_range, dt=0.1)
        health_after_second = self.mouse.health
        
        # Health should decrease with each update
        self.assertLess(health_after_second, health_after_first)

    def test_framerate_independence(self) -> None:
        """Test that health transfer scales with delta time."""
        catch_range = 100.0
        self.kitten.x = self.mouse.x
        self.kitten.y = self.mouse.y
        
        # Test with dt = 0.5
        mouse1 = Mouse(x=0.0, y=0.0, health=CONFIG.MAX_HEALTH)
        mouse1.width = 32.0
        mouse1.height = 32.0
        kitten1 = Kitten(x=0.0, y=0.0, stamina=CONFIG.MAX_STAMINA)
        kitten1.width = 32.0
        kitten1.height = 32.0
        
        update_health_stamina(mouse1, kitten1, catch_range=catch_range, dt=0.5)
        health_loss_1 = CONFIG.MAX_HEALTH - mouse1.health
        
        # Test with dt = 1.0
        mouse2 = Mouse(x=0.0, y=0.0, health=CONFIG.MAX_HEALTH)
        mouse2.width = 32.0
        mouse2.height = 32.0
        kitten2 = Kitten(x=0.0, y=0.0, stamina=CONFIG.MAX_STAMINA)
        kitten2.width = 32.0
        kitten2.height = 32.0
        
        update_health_stamina(mouse2, kitten2, catch_range=catch_range, dt=1.0)
        health_loss_2 = CONFIG.MAX_HEALTH - mouse2.health
        
        # Health loss with dt=1.0 should be approximately double that of dt=0.5
        self.assertAlmostEqual(health_loss_2, health_loss_1 * 2.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
