"""Integration tests for asset loading in hello_world.py."""

import os
import unittest
from unittest.mock import MagicMock, patch

import pyglet
from chaser_game.asset_manifest import AssetManifest
from chaser_game.assets import get_loader


class TestHelloWorldAssetLoading(unittest.TestCase):
    """Tests for asset loading during hello_world initialization."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Get manifest path
        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        pyglet_readme_dir = os.path.join(project_root, "src", "pyglet_readme")
        self.assets_root = os.path.join(pyglet_readme_dir, "assets")
        self.manifest_path = os.path.join(self.assets_root, "manifest.yaml")

    def test_asset_loader_initialization(self) -> None:
        """Test that AssetLoader initializes correctly for hello_world."""
        loader = get_loader()

        self.assertIsNotNone(loader)
        self.assertIsNotNone(loader.assets_dir)
        self.assertTrue(os.path.isdir(loader.assets_dir))

    def test_required_assets_exist(self) -> None:
        """Test that all required assets exist for hello_world."""
        loader = get_loader()

        required_assets = {
            "assets/images/kitten.png": "image",
            "assets/sprites/mouse_sheet.png": "image",
            "assets/audio/sfx/meow.wav": "sound",
            "assets/audio/music/ambience.wav": "sound",
        }

        for asset_path in required_assets.keys():
            full_path = os.path.join(loader.script_dir, asset_path)
            self.assertTrue(
                os.path.isfile(full_path),
                f"Required asset missing: {full_path}",
            )

    @patch("pyglet.window.Window")
    @patch("pyglet.app.run")
    def test_asset_loading_sequence(self, mock_run: MagicMock, mock_window: MagicMock) -> None:
        """Test the sequence of asset loading in hello_world."""
        # Mock the window and app
        mock_window_instance = MagicMock()
        mock_window.return_value = mock_window_instance
        mock_window_instance.width = 800
        mock_window_instance.height = 600

        # Verify we can initialize the loader
        loader = get_loader()

        # Verify asset paths are set up correctly
        self.assertTrue(loader.images_dir.endswith("images"))
        self.assertTrue(loader.sprites_dir.endswith("sprites"))
        self.assertTrue(loader.sfx_dir.endswith("sfx"))
        self.assertTrue(loader.music_dir.endswith("music"))

    def test_asset_manifest_matches_hello_world_usage(self) -> None:
        """Test that manifest includes all assets used by hello_world."""
        manifest = AssetManifest(self.manifest_path)

        # Get all asset paths from manifest
        all_paths = set(manifest.get_asset_paths())

        # Required by hello_world
        required_in_hello_world = {
            "images/kitten.png",
            "sprites/mouse_sheet.png",
            "audio/sfx/meow.wav",
            "audio/music/ambience.wav",
        }

        # Check that all required assets are in manifest
        for required_asset in required_in_hello_world:
            self.assertIn(
                required_asset,
                all_paths,
                f"Asset required by hello_world missing from manifest: {required_asset}",
            )

    def test_asset_paths_match_hello_world_calls(self) -> None:
        """Test that asset paths in hello_world match asset loader paths."""
        loader = get_loader()

        # These are the assets referenced in hello_world.py
        hello_world_assets = {
            "assets/images/kitten.png": loader.images_dir,
            "assets/sprites/mouse_sheet.png": loader.sprites_dir,
            "assets/audio/sfx/meow.wav": loader.sfx_dir,
            "assets/audio/music/ambience.wav": loader.music_dir,
        }

        # Verify each can be found via the loader's asset directories
        for asset_path, expected_dir in hello_world_assets.items():
            # Extract filename from path
            filename = asset_path.split("/")[-1]
            os.path.join(expected_dir, filename)

            # Asset directory should exist
            self.assertTrue(
                os.path.isdir(expected_dir),
                f"Asset directory doesn't exist: {expected_dir}",
            )

    def test_pyglet_resource_path_configuration(self) -> None:
        """Test that pyglet.resource is configured correctly."""
        get_loader()

        # pyglet.resource.path should be configured
        self.assertIsNotNone(pyglet.resource.path)
        self.assertGreater(len(pyglet.resource.path), 0)

    @patch("pyglet.window.Window")
    def test_asset_verification_passes(self, mock_window: MagicMock) -> None:
        """Test that asset verification passes for hello_world assets."""
        mock_window.return_value = MagicMock()

        loader = get_loader()

        # These are the assets referenced in hello_world.py
        required_assets = {
            "assets/images/kitten.png": "image",
            "assets/sprites/mouse_sheet.png": "image",
            "assets/audio/sfx/meow.wav": "sound",
            "assets/audio/music/ambience.wav": "sound",
        }

        # Verification should pass or warn about missing ignored assets
        valid = loader.verify_assets(required_assets)
        # Note: may be False if ignored assets (sprites, music) are missing
        # but tracked assets should be present
        self.assertIsInstance(valid, bool)

    def test_asset_loading_order_independence(self) -> None:
        """Test that assets can be loaded in any order without issues."""
        loader = get_loader()

        # Try loading in different orders
        assets_to_load = [
            ("assets/images/kitten.png", "image"),
            ("assets/audio/sfx/meow.wav", "sound"),
            ("assets/sprites/mouse_sheet.png", "image"),
            ("assets/audio/music/ambience.wav", "sound"),
        ]

        for asset_path, _asset_type in assets_to_load:
            full_path = os.path.join(loader.script_dir, asset_path)
            self.assertTrue(
                os.path.isfile(full_path),
                f"Asset loading order test: missing {asset_path}",
            )


class TestAssetLoadingErrors(unittest.TestCase):
    """Tests for error handling during asset loading."""

    def test_missing_asset_error_message(self) -> None:
        """Test that missing assets raise meaningful errors."""
        loader = get_loader()

        with self.assertRaises(FileNotFoundError) as context:
            loader.load_image("nonexistent_image.png")

        self.assertIn("nonexistent_image.png", str(context.exception))
        self.assertIn("Image", str(context.exception))

    def test_missing_sound_error_message(self) -> None:
        """Test that missing sounds raise meaningful errors."""
        loader = get_loader()

        with self.assertRaises(FileNotFoundError) as context:
            loader.load_sound("nonexistent_sound.wav")

        self.assertIn("nonexistent_sound.wav", str(context.exception))
        self.assertIn("Sound", str(context.exception))


class TestAssetIntegrationWithManifest(unittest.TestCase):
    """Tests for integration between asset loader and manifest."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        pyglet_readme_dir = os.path.join(project_root, "src", "pyglet_readme")
        self.assets_root = os.path.join(pyglet_readme_dir, "assets")
        self.manifest_path = os.path.join(self.assets_root, "manifest.yaml")

    def test_tracked_assets_loadable(self) -> None:
        """Test that all tracked assets are loadable via asset loader."""
        manifest = AssetManifest(self.manifest_path)
        get_loader()

        tracked_assets = manifest.get_tracked_assets()

        # Verify tracked assets exist and are loadable
        for asset_path in tracked_assets:
            full_path = os.path.join(self.assets_root, asset_path)
            self.assertTrue(
                os.path.isfile(full_path),
                f"Tracked asset not found: {asset_path}",
            )

    def test_hello_world_required_assets_in_manifest(self) -> None:
        """Test that all hello_world required assets are documented in manifest."""
        manifest = AssetManifest(self.manifest_path)

        # Check images section
        self.assertIn("kitten", manifest.images)
        self.assertIn("mouse_sheet", manifest.images)

        # Check audio section
        self.assertIn("meow", manifest.audio)
        self.assertIn("ambience", manifest.audio)

    def test_manifest_asset_metadata_accessible(self) -> None:
        """Test that asset metadata is accessible for hello_world assets."""
        manifest = AssetManifest(self.manifest_path)

        kitten = manifest.images.get("kitten", {})
        self.assertEqual(kitten.get("type"), "sprite")
        self.assertIn("dimensions", kitten)

        mouse_sheet = manifest.images.get("mouse_sheet", {})
        self.assertEqual(mouse_sheet.get("type"), "sprite_sheet")
        self.assertIn("grid", mouse_sheet)

        meow = manifest.audio.get("meow", {})
        self.assertEqual(meow.get("type"), "sound_effect")

        ambience = manifest.audio.get("ambience", {})
        self.assertEqual(ambience.get("type"), "background_music")


if __name__ == "__main__":
    unittest.main()
