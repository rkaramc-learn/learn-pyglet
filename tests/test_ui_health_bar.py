"""Tests for the HealthBar UI component."""

import unittest
from unittest.mock import MagicMock, patch

from chaser_game.config import CONFIG
from chaser_game.ui.health_bar import HealthBar


class TestHealthBar(unittest.TestCase):
    """Test the HealthBar UI component."""

    def test_health_bar_creation_defaults(self) -> None:
        """Test creating a health bar with default values."""
        bar = HealthBar()
        self.assertEqual(bar.max_value, CONFIG.MAX_HEALTH)
        self.assertEqual(bar.width, CONFIG.BAR_WIDTH)
        self.assertEqual(bar.height, CONFIG.BAR_HEIGHT)

    def test_health_bar_creation_custom_values(self) -> None:
        """Test creating a health bar with custom values."""
        bar = HealthBar(max_value=200.0, width=100, height=10, x=50.0, y=75.0)
        self.assertEqual(bar.max_value, 200.0)
        self.assertEqual(bar.width, 100)
        self.assertEqual(bar.height, 10)

    def test_health_bar_initial_position(self) -> None:
        """Test that health bar is positioned correctly on creation."""
        bar = HealthBar(x=100.0, y=200.0)
        self.assertEqual(bar.background.x, 100.0)
        self.assertEqual(bar.background.y, 200.0)
        self.assertEqual(bar.foreground.x, 100.0)
        self.assertEqual(bar.foreground.y, 200.0)

    def test_health_bar_update_full_health(self) -> None:
        """Test health bar at full value."""
        bar = HealthBar(max_value=100.0, width=100)
        bar.update(current_value=100.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 100)
        # Color is set by pyglet shapes, includes alpha channel
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_GREEN)

    def test_health_bar_update_half_health(self) -> None:
        """Test health bar at half value."""
        bar = HealthBar(max_value=100.0, width=100)
        bar.update(current_value=50.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 50)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_GREEN)

    def test_health_bar_update_zero_health(self) -> None:
        """Test health bar at zero value."""
        bar = HealthBar(max_value=100.0, width=100)
        bar.update(current_value=0.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 0)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_RED)

    def test_health_bar_color_change_threshold(self) -> None:
        """Test that bar color changes at threshold."""
        bar = HealthBar(max_value=100.0, width=100)
        
        # Above threshold should be green
        bar.update(current_value=40.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_GREEN)
        
        # At/below threshold should be red
        bar.update(current_value=30.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_RED)

    def test_health_bar_color_change_just_above_threshold(self) -> None:
        """Test color change just above low health threshold."""
        bar = HealthBar(max_value=100.0, width=100)
        
        # Just above threshold (30.1)
        bar.update(current_value=30.1, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_GREEN)
        
        # At threshold (30.0)
        bar.update(current_value=30.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_RED)

    def test_health_bar_clamps_above_max(self) -> None:
        """Test that bar clamps values above max."""
        bar = HealthBar(max_value=100.0, width=100)
        bar.update(current_value=150.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 100)

    def test_health_bar_clamps_below_zero(self) -> None:
        """Test that bar clamps negative values."""
        bar = HealthBar(max_value=100.0, width=100)
        bar.update(current_value=-50.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 0)

    def test_health_bar_update_position(self) -> None:
        """Test updating bar position."""
        bar = HealthBar(x=0.0, y=0.0)
        bar.update(current_value=50.0, x=100.0, y=200.0)
        self.assertEqual(bar.background.x, 100.0)
        self.assertEqual(bar.background.y, 200.0)
        self.assertEqual(bar.foreground.x, 100.0)
        self.assertEqual(bar.foreground.y, 200.0)

    def test_health_bar_set_position(self) -> None:
        """Test setting bar position directly."""
        bar = HealthBar()
        bar.set_position(150.0, 250.0)
        self.assertEqual(bar.background.x, 150.0)
        self.assertEqual(bar.background.y, 250.0)
        self.assertEqual(bar.foreground.x, 150.0)
        self.assertEqual(bar.foreground.y, 250.0)

    def test_health_bar_get_position(self) -> None:
        """Test getting bar position."""
        bar = HealthBar(x=100.0, y=200.0)
        pos = bar.get_position()
        self.assertEqual(pos, (100.0, 200.0))

    def test_health_bar_get_position_after_update(self) -> None:
        """Test getting position after update."""
        bar = HealthBar(x=0.0, y=0.0)
        bar.update(current_value=50.0, x=75.0, y=125.0)
        pos = bar.get_position()
        self.assertEqual(pos, (75.0, 125.0))

    def test_health_bar_with_stamina_max(self) -> None:
        """Test health bar with stamina max value."""
        bar = HealthBar(max_value=CONFIG.MAX_STAMINA, width=100)
        bar.update(current_value=CONFIG.MAX_STAMINA, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 100)

    def test_health_bar_with_stamina_values(self) -> None:
        """Test health bar with various stamina values."""
        bar = HealthBar(max_value=CONFIG.MAX_STAMINA, width=100)
        
        # 50% stamina
        bar.update(current_value=50.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 50)
        
        # 25% stamina
        bar.update(current_value=25.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 25)

    def test_health_bar_draw(self) -> None:
        """Test that draw method can be called without error."""
        with patch("pyglet.shapes.Rectangle.draw"):
            bar = HealthBar()
            bar.update(current_value=50.0, x=0.0, y=0.0)
            # Should not raise an exception
            bar.draw()

    def test_health_bar_sequential_updates(self) -> None:
        """Test multiple sequential updates."""
        bar = HealthBar(max_value=100.0, width=100)
        
        # Update 1: 100% health
        bar.update(current_value=100.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 100)
        
        # Update 2: 50% health
        bar.update(current_value=50.0, x=10.0, y=10.0)
        self.assertEqual(bar.foreground.width, 50)
        self.assertEqual(bar.background.x, 10.0)
        
        # Update 3: 10% health (below threshold)
        bar.update(current_value=10.0, x=20.0, y=20.0)
        self.assertEqual(bar.foreground.width, 10)
        self.assertEqual(bar.foreground.color[:3], CONFIG.COLOR_RED)

    def test_health_bar_precise_width_calculation(self) -> None:
        """Test precise width calculation for various values."""
        bar = HealthBar(max_value=100.0, width=200)
        
        # Test 25%, 50%, 75%
        bar.update(current_value=25.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 50)
        
        bar.update(current_value=50.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 100)
        
        bar.update(current_value=75.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 150)

    def test_health_bar_with_odd_dimensions(self) -> None:
        """Test health bar with non-standard dimensions."""
        bar = HealthBar(max_value=77.0, width=77)
        bar.update(current_value=77.0, x=0.0, y=0.0)
        self.assertEqual(bar.foreground.width, 77)
        
        bar.update(current_value=38.5, x=0.0, y=0.0)
        self.assertAlmostEqual(bar.foreground.width, 38.5, places=1)


if __name__ == "__main__":
    unittest.main()
