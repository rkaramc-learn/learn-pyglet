"""Tests for the configuration module."""

import unittest

from pyglet_readme.config import CONFIG, GameConfig


class TestGameConfig(unittest.TestCase):
    """Test the GameConfig dataclass."""

    def test_config_creation(self) -> None:
        """Test creating a GameConfig instance with defaults."""
        config = GameConfig()
        self.assertEqual(config.WINDOW_WIDTH, 800)
        self.assertEqual(config.WINDOW_HEIGHT, 600)
        self.assertEqual(config.TARGET_FPS, 60.0)

    def test_config_is_frozen(self) -> None:
        """Test that GameConfig is frozen (immutable)."""
        config = GameConfig()
        with self.assertRaises(AttributeError):
            config.WINDOW_WIDTH = 1024  # type: ignore[misc]

    def test_config_movement_constants(self) -> None:
        """Test movement-related constants."""
        config = GameConfig()
        self.assertEqual(config.WINDOW_TRAVERSAL_TIME, 10.0)
        self.assertEqual(config.KITTEN_SPEED_FACTOR, 1.5)
        self.assertAlmostEqual(config.DIAGONAL_MOVEMENT_FACTOR, 0.7071, places=4)
        self.assertEqual(config.MOVEMENT_DISTANCE_THRESHOLD, 2.0)

    def test_config_health_constants(self) -> None:
        """Test health and stamina constants."""
        config = GameConfig()
        self.assertEqual(config.MAX_HEALTH, 100.0)
        self.assertEqual(config.MAX_STAMINA, 100.0)
        self.assertEqual(config.BASE_DRAIN_RATE, 20.0)
        self.assertEqual(config.PASSIVE_STAMINA_DRAIN, 2.0)
        self.assertEqual(config.LOW_HEALTH_THRESHOLD, 30.0)

    def test_config_ui_constants(self) -> None:
        """Test UI bar configuration."""
        config = GameConfig()
        self.assertEqual(config.BAR_WIDTH, 50)
        self.assertEqual(config.BAR_HEIGHT, 5)
        self.assertEqual(config.BAR_OFFSET, 20)

    def test_config_colors(self) -> None:
        """Test color constants are RGB tuples."""
        config = GameConfig()
        self.assertEqual(config.COLOR_DARK_GRAY, (50, 50, 50))
        self.assertEqual(config.COLOR_GREEN, (0, 255, 0))
        self.assertEqual(config.COLOR_RED, (255, 0, 0))

    def test_config_asset_paths(self) -> None:
        """Test asset path constants."""
        config = GameConfig()
        self.assertEqual(config.ASSET_KITTEN_IMAGE, "assets/images/kitten.png")
        self.assertEqual(config.ASSET_MOUSE_SHEET, "assets/sprites/mouse_sheet.png")
        self.assertEqual(config.ASSET_MEOW_SOUND, "assets/audio/sfx/meow.wav")
        self.assertEqual(config.ASSET_AMBIENCE_MUSIC, "assets/audio/music/ambience.wav")

    def test_config_ui_text(self) -> None:
        """Test UI text constants."""
        config = GameConfig()
        self.assertEqual(config.TEXT_HELLO_WORLD, "Hello, world!")

    def test_global_config_instance(self) -> None:
        """Test that global CONFIG instance exists and is valid."""
        self.assertIsInstance(CONFIG, GameConfig)
        self.assertEqual(CONFIG.WINDOW_WIDTH, 800)
        self.assertEqual(CONFIG.MAX_HEALTH, 100.0)

    def test_config_with_custom_values(self) -> None:
        """Test creating config with custom values."""
        custom_config = GameConfig(WINDOW_WIDTH=1024, MAX_HEALTH=150.0)
        self.assertEqual(custom_config.WINDOW_WIDTH, 1024)
        self.assertEqual(custom_config.MAX_HEALTH, 150.0)
        # Other values should still be defaults
        self.assertEqual(custom_config.WINDOW_HEIGHT, 600)


if __name__ == "__main__":
    unittest.main()
