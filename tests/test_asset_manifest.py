"""Unit tests for AssetManifest class."""

import os
import tempfile
import unittest
from pathlib import Path

import yaml
from chaser_game.asset_manifest import AssetManifest


class TestAssetManifest(unittest.TestCase):
    """Tests for AssetManifest parsing and validation."""

    def setUp(self) -> None:
        """Create temporary manifest file for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manifest_path = os.path.join(self.temp_dir.name, "manifest.yaml")

        # Create a test manifest
        self.test_manifest = {
            "version": "1.0",
            "images": {
                "kitten": {
                    "path": "assets/images/kitten.png",
                    "type": "sprite",
                    "dimensions": [104, 104],
                    "tracked": True,
                    "description": "Player kitten",
                },
                "mouse_sheet": {
                    "path": "assets/sprites/mouse_sheet.png",
                    "type": "sprite_sheet",
                    "grid": [10, 10],
                    "tracked": False,
                    "description": "Mouse animation sheet",
                },
            },
            "audio": {
                "meow": {
                    "path": "assets/audio/sfx/meow.wav",
                    "type": "sound_effect",
                    "tracked": True,
                    "description": "Meow sound",
                },
                "ambience": {
                    "path": "assets/audio/music/ambience.wav",
                    "type": "background_music",
                    "tracked": False,
                    "description": "Background music",
                },
            },
            "source": {
                "mouse_video": {
                    "path": "assets/source/mouse.mp4",
                    "type": "video_source",
                    "tracked": False,
                    "description": "Source video",
                },
            },
        }

        with open(self.manifest_path, "w") as f:
            yaml.dump(self.test_manifest, f)

    def tearDown(self) -> None:
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_manifest_loading(self) -> None:
        """Test that manifest loads correctly."""
        manifest = AssetManifest(self.manifest_path)

        self.assertEqual(manifest.version, "1.0")
        self.assertIsNotNone(manifest.images)
        self.assertIsNotNone(manifest.audio)
        self.assertIsNotNone(manifest.source)

    def test_get_asset_paths(self) -> None:
        """Test retrieving all asset paths."""
        manifest = AssetManifest(self.manifest_path)
        paths = manifest.get_asset_paths()

        self.assertEqual(len(paths), 5)
        self.assertIn("assets/images/kitten.png", paths)
        self.assertIn("assets/sprites/mouse_sheet.png", paths)
        self.assertIn("assets/audio/sfx/meow.wav", paths)
        self.assertIn("assets/audio/music/ambience.wav", paths)
        self.assertIn("assets/source/mouse.mp4", paths)

    def test_get_tracked_assets(self) -> None:
        """Test retrieving only tracked assets."""
        manifest = AssetManifest(self.manifest_path)
        tracked = manifest.get_tracked_assets()

        self.assertEqual(len(tracked), 2)
        self.assertIn("assets/images/kitten.png", tracked)
        self.assertIn("assets/audio/sfx/meow.wav", tracked)
        self.assertNotIn("assets/sprites/mouse_sheet.png", tracked)
        self.assertNotIn("assets/audio/music/ambience.wav", tracked)

    def test_get_ignored_assets(self) -> None:
        """Test retrieving only ignored assets."""
        manifest = AssetManifest(self.manifest_path)
        ignored = manifest.get_ignored_assets()

        self.assertEqual(len(ignored), 3)
        self.assertIn("assets/sprites/mouse_sheet.png", ignored)
        self.assertIn("assets/audio/music/ambience.wav", ignored)
        self.assertIn("assets/source/mouse.mp4", ignored)
        self.assertNotIn("assets/images/kitten.png", ignored)
        self.assertNotIn("assets/audio/sfx/meow.wav", ignored)

    def test_validate_assets_all_present(self) -> None:
        """Test validation when all tracked assets exist."""
        # Create the tracked asset files
        os.makedirs(os.path.join(self.temp_dir.name, "assets/images"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir.name, "assets/audio/sfx"), exist_ok=True)

        Path(os.path.join(self.temp_dir.name, "assets/images/kitten.png")).touch()
        Path(os.path.join(self.temp_dir.name, "assets/audio/sfx/meow.wav")).touch()

        manifest = AssetManifest(self.manifest_path)
        valid, missing = manifest.validate_assets(self.temp_dir.name)

        self.assertTrue(valid)
        self.assertEqual(len(missing), 0)

    def test_validate_assets_missing(self) -> None:
        """Test validation when tracked assets are missing."""
        manifest = AssetManifest(self.manifest_path)
        valid, missing = manifest.validate_assets(self.temp_dir.name)

        self.assertFalse(valid)
        self.assertEqual(len(missing), 2)
        self.assertIn("assets/images/kitten.png", missing)
        self.assertIn("assets/audio/sfx/meow.wav", missing)

    def test_manifest_not_found(self) -> None:
        """Test that FileNotFoundError is raised for missing manifest."""
        with self.assertRaises(FileNotFoundError):
            AssetManifest("/nonexistent/path/manifest.yaml")

    def test_manifest_metadata_access(self) -> None:
        """Test accessing asset metadata from parsed manifest."""
        manifest = AssetManifest(self.manifest_path)

        # Access image metadata
        kitten = manifest.images.get("kitten", {})
        self.assertEqual(kitten.get("type"), "sprite")
        self.assertEqual(kitten.get("dimensions"), [104, 104])
        self.assertTrue(kitten.get("tracked"))

        # Access audio metadata
        meow = manifest.audio.get("meow", {})
        self.assertEqual(meow.get("type"), "sound_effect")
        self.assertTrue(meow.get("tracked"))

        # Access source metadata
        mouse_video = manifest.source.get("mouse_video", {})
        self.assertEqual(mouse_video.get("type"), "video_source")
        self.assertFalse(mouse_video.get("tracked"))

    def test_asset_description_preserved(self) -> None:
        """Test that asset descriptions are preserved in manifest."""
        manifest = AssetManifest(self.manifest_path)

        kitten = manifest.images.get("kitten", {})
        self.assertEqual(kitten.get("description"), "Player kitten")

        meow = manifest.audio.get("meow", {})
        self.assertEqual(meow.get("description"), "Meow sound")

    def test_empty_manifest(self) -> None:
        """Test handling of empty manifest."""
        empty_path = os.path.join(self.temp_dir.name, "empty.yaml")
        with open(empty_path, "w") as f:
            f.write("---\n")  # Empty YAML

        manifest = AssetManifest(empty_path)

        self.assertEqual(len(manifest.get_asset_paths()), 0)
        self.assertEqual(len(manifest.get_tracked_assets()), 0)
        self.assertEqual(len(manifest.get_ignored_assets()), 0)


class TestAssetManifestIntegration(unittest.TestCase):
    """Integration tests using actual project manifest."""

    def test_load_project_manifest(self) -> None:
        """Test loading the actual project manifest.yaml."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../src/chaser_game/assets/manifest.yaml",
        )

        if not os.path.exists(manifest_path):
            self.skipTest("Project manifest not found")

        manifest = AssetManifest(manifest_path)

        self.assertIsNotNone(manifest.version)
        paths = manifest.get_asset_paths()
        self.assertGreater(len(paths), 0)

    def test_project_manifest_has_tracked_assets(self) -> None:
        """Test that project manifest has tracked assets."""
        manifest_path = os.path.join(
            os.path.dirname(__file__),
            "../src/chaser_game/assets/manifest.yaml",
        )

        if not os.path.exists(manifest_path):
            self.skipTest("Project manifest not found")

        manifest = AssetManifest(manifest_path)
        tracked = manifest.get_tracked_assets()

        self.assertGreater(len(tracked), 0, "Project should have tracked assets")


if __name__ == "__main__":
    unittest.main()
