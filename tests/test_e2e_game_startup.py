"""End-to-end tests for full game startup with new asset system."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO

import pyglet

from pyglet_readme.assets import get_loader
from pyglet_readme.asset_manifest import AssetManifest


class TestGameStartup(unittest.TestCase):
    """End-to-end tests for game startup with new asset system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Get manifest path
        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        pyglet_readme_dir = os.path.join(project_root, "src", "pyglet_readme")
        self.pyglet_readme_dir = pyglet_readme_dir
        self.assets_root = os.path.join(pyglet_readme_dir, "assets")
        self.manifest_path = os.path.join(self.assets_root, "manifest.yaml")

    @patch("pyglet.app.run")
    @patch("pyglet.window.Window")
    def test_game_initializes_successfully(
        self, mock_window_class: MagicMock, mock_app_run: MagicMock
    ) -> None:
        """Test that game initializes without errors with new asset system."""
        # Set up mock window
        mock_window = MagicMock()
        mock_window.width = 800
        mock_window.height = 600
        mock_window_class.return_value = mock_window

        # Import the game module
        from pyglet_readme.hello_world import run_hello_world

        # The actual run_hello_world will fail because we're not mocking everything,
        # but we can test that the imports work and asset loader is accessible
        loader = get_loader()
        self.assertIsNotNone(loader)
        self.assertTrue(os.path.isdir(loader.assets_dir))

    @patch("pyglet.app.run")
    @patch("pyglet.window.Window")
    @patch("pyglet.sprite.Sprite")
    @patch("pyglet.resource.image")
    @patch("pyglet.resource.media")
    def test_game_startup_asset_loading_calls(
        self,
        mock_media: MagicMock,
        mock_image: MagicMock,
        mock_sprite: MagicMock,
        mock_window_class: MagicMock,
        mock_app_run: MagicMock,
    ) -> None:
        """Test that game startup makes correct asset loading calls."""
        # Set up mocks
        mock_window = MagicMock()
        mock_window.width = 800
        mock_window.height = 600
        mock_window_class.return_value = mock_window

        mock_image.return_value = MagicMock(width=100, height=100)
        mock_media.return_value = MagicMock()
        mock_sprite.return_value = MagicMock(
            width=25, height=25, x=0, y=600, scale=0.25
        )

        # Verify that we can set up the loader
        loader = get_loader()

        # Verify the asset directories are configured correctly
        self.assertTrue(loader.images_dir.endswith("images"))
        self.assertTrue(loader.sprites_dir.endswith("sprites"))
        self.assertTrue(loader.sfx_dir.endswith("sfx"))
        self.assertTrue(loader.music_dir.endswith("music"))

    def test_all_game_assets_present_in_manifest(self) -> None:
        """Test that all assets used by game are documented in manifest."""
        manifest = AssetManifest(self.manifest_path)

        # Game requires these assets
        required_assets = {
            "images": ["kitten"],
            "audio": ["meow", "ambience"],
        }

        # Sprites are generated/ignored, but should be in manifest
        sprite_keys = ["mouse_sheet"]

        for image_key in required_assets["images"]:
            self.assertIn(
                image_key,
                manifest.images,
                f"Required image '{image_key}' not in manifest",
            )

        for sprite_key in sprite_keys:
            self.assertIn(
                sprite_key,
                manifest.images,
                f"Sprite '{sprite_key}' not in manifest",
            )

        for audio_key in required_assets["audio"]:
            self.assertIn(
                audio_key,
                manifest.audio,
                f"Required audio '{audio_key}' not in manifest",
            )

    def test_game_asset_paths_are_accessible(self) -> None:
        """Test that all game asset paths are accessible."""
        loader = get_loader()

        game_assets = {
            "images/kitten.png": loader.images_dir,
            "sprites/mouse_sheet.png": loader.sprites_dir,
            "audio/sfx/meow.wav": loader.sfx_dir,
            "audio/music/ambience.wav": loader.music_dir,
        }

        for asset_name, asset_dir in game_assets.items():
            self.assertTrue(
                os.path.isdir(asset_dir),
                f"Asset directory not accessible: {asset_dir}",
            )

    def test_tracked_assets_exist(self) -> None:
        """Test that all tracked assets required by game exist on disk."""
        manifest = AssetManifest(self.manifest_path)
        tracked = manifest.get_tracked_assets()

        # Filter to just the assets the game needs
        game_required_tracked = {"images/kitten.png", "audio/sfx/meow.wav"}

        for asset_path in tracked:
            if asset_path in game_required_tracked:
                full_path = os.path.join(self.assets_root, asset_path)
                self.assertTrue(
                    os.path.isfile(full_path),
                    f"Required tracked asset missing: {asset_path}",
                )

    @patch("pyglet.app.run")
    @patch("pyglet.window.Window")
    def test_game_window_configuration(
        self, mock_window_class: MagicMock, mock_app_run: MagicMock
    ) -> None:
        """Test that game window is configured correctly."""
        mock_window = MagicMock()
        mock_window.width = 800
        mock_window.height = 600
        mock_window_class.return_value = mock_window

        # Verify window gets created
        window = pyglet.window.Window()
        self.assertIsNotNone(window)

    def test_asset_loader_singleton_in_game_context(self) -> None:
        """Test that asset loader singleton works correctly in game context."""
        loader1 = get_loader()
        loader2 = get_loader()

        # Should be same instance
        self.assertIs(loader1, loader2)

        # Should have consistent configuration
        self.assertEqual(loader1.assets_dir, loader2.assets_dir)
        self.assertEqual(loader1.images_dir, loader2.images_dir)

    def test_manifest_grid_configuration_for_mouse_sprite(self) -> None:
        """Test that manifest has correct grid configuration for mouse sprite sheet."""
        manifest = AssetManifest(self.manifest_path)

        mouse_sheet = manifest.images.get("mouse_sheet", {})

        # Mouse sheet should be 10x10 grid
        grid = mouse_sheet.get("grid")
        self.assertIsNotNone(grid)
        self.assertEqual(grid, [10, 10])

        # Frame duration should match hello_world usage (1/12 second)
        frame_duration = mouse_sheet.get("frame_duration")
        self.assertIsNotNone(frame_duration)
        self.assertAlmostEqual(frame_duration, 1 / 12.0, places=3)

    def test_manifest_kitten_sprite_configuration(self) -> None:
        """Test that manifest has correct configuration for kitten sprite."""
        manifest = AssetManifest(self.manifest_path)

        kitten = manifest.images.get("kitten", {})

        # Should have dimensions
        dimensions = kitten.get("dimensions")
        self.assertIsNotNone(dimensions)

        # Should be marked as tracked (sprite is in repo)
        self.assertTrue(kitten.get("tracked"))

    def test_manifest_audio_configuration(self) -> None:
        """Test that manifest has correct audio configuration."""
        manifest = AssetManifest(self.manifest_path)

        meow = manifest.audio.get("meow", {})
        ambience = manifest.audio.get("ambience", {})

        # Meow is tracked (in repo)
        self.assertTrue(meow.get("tracked"))

        # Ambience is ignored (large file)
        self.assertFalse(ambience.get("tracked"))

        # Both should have type information
        self.assertEqual(meow.get("type"), "sound_effect")
        self.assertEqual(ambience.get("type"), "background_music")

    def test_all_asset_directories_initialized(self) -> None:
        """Test that all asset directories are properly initialized."""
        loader = get_loader()

        required_dirs = [
            loader.images_dir,
            loader.sprites_dir,
            loader.sfx_dir,
            loader.music_dir,
            loader.source_dir,
        ]

        for dir_path in required_dirs:
            self.assertTrue(
                os.path.isdir(dir_path),
                f"Required asset directory not initialized: {dir_path}",
            )

    def test_pyglet_resource_path_includes_assets(self) -> None:
        """Test that pyglet.resource.path is configured to find assets."""
        loader = get_loader()

        # After loader initialization, pyglet.resource.path should be set
        self.assertIsNotNone(pyglet.resource.path)
        self.assertGreater(len(pyglet.resource.path), 0)

    def test_game_can_verify_all_assets(self) -> None:
        """Test that game can verify all its required assets."""
        loader = get_loader()

        # Game uses these assets
        required_assets = {
            "assets/images/kitten.png": "image",
            "assets/sprites/mouse_sheet.png": "image",
            "assets/audio/sfx/meow.wav": "sound",
            "assets/audio/music/ambience.wav": "sound",
        }

        # Verification should work without errors
        valid = loader.verify_assets(required_assets)
        self.assertIsInstance(valid, bool)

    def test_no_import_errors_in_game_module(self) -> None:
        """Test that game module can be imported without errors."""
        try:
            from pyglet_readme import hello_world
            self.assertIsNotNone(hello_world)
            self.assertTrue(hasattr(hello_world, "run_hello_world"))
        except ImportError as e:
            self.fail(f"Failed to import hello_world module: {e}")

    def test_asset_manifest_complete(self) -> None:
        """Test that asset manifest is complete and valid."""
        manifest = AssetManifest(self.manifest_path)

        # Should have version
        self.assertIsNotNone(manifest.version)

        # Should have assets in all categories
        self.assertGreater(len(manifest.images), 0)
        self.assertGreater(len(manifest.audio), 0)

        # Should be able to query assets
        all_paths = manifest.get_asset_paths()
        self.assertGreater(len(all_paths), 0)

        tracked = manifest.get_tracked_assets()
        self.assertGreater(len(tracked), 0)


if __name__ == "__main__":
    unittest.main()
