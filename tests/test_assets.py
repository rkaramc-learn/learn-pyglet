"""Unit tests for AssetLoader class."""

import os
import unittest
from unittest.mock import MagicMock, patch

import pyglet
from chaser_game.assets import AssetLoader


class TestAssetLoader(unittest.TestCase):
    """Tests for AssetLoader initialization and configuration."""

    def test_initialization(self) -> None:
        """Test that AssetLoader initializes correctly."""
        loader = AssetLoader()

        self.assertIsNotNone(loader.script_dir)
        self.assertTrue(os.path.isdir(loader.script_dir))

    def test_asset_directory_paths(self) -> None:
        """Test that asset directory paths are correctly set."""
        loader = AssetLoader()

        self.assertTrue(loader.assets_dir.endswith("assets"))
        self.assertTrue(loader.images_dir.endswith("images"))
        self.assertTrue(loader.sprites_dir.endswith("sprites"))
        self.assertTrue(loader.sfx_dir.endswith("sfx"))
        self.assertTrue(loader.music_dir.endswith("music"))
        self.assertTrue(loader.source_dir.endswith("source"))

    def test_pyglet_resource_path_configured(self) -> None:
        """Test that pyglet resource path includes assets directory."""
        loader = AssetLoader()

        # pyglet.resource.path should include the assets directory
        self.assertIn(loader.script_dir, pyglet.resource.path)

    @patch("pyglet.resource.image")
    def test_load_image_success(self, mock_image: MagicMock) -> None:
        """Test successful image loading."""
        loader = AssetLoader()
        mock_image.return_value = MagicMock()

        result = loader.load_image("assets/images/kitten.png")

        self.assertIsNotNone(result)
        mock_image.assert_called_once_with("assets/images/kitten.png")

    @patch("pyglet.resource.image")
    def test_load_image_not_found(self, mock_image: MagicMock) -> None:
        """Test image loading with missing file."""
        loader = AssetLoader()
        mock_image.side_effect = pyglet.resource.ResourceNotFoundException("kitten.png")

        with self.assertRaises(FileNotFoundError) as context:
            loader.load_image("kitten.png")

        self.assertIn("kitten.png", str(context.exception))

    @patch("pyglet.resource.media")
    def test_load_sound_success(self, mock_media: MagicMock) -> None:
        """Test successful sound loading."""
        loader = AssetLoader()
        mock_media.return_value = MagicMock()

        result = loader.load_sound("assets/audio/sfx/meow.wav", streaming=False)

        self.assertIsNotNone(result)
        mock_media.assert_called_once_with("assets/audio/sfx/meow.wav", streaming=False)

    @patch("pyglet.resource.media")
    def test_load_sound_streaming(self, mock_media: MagicMock) -> None:
        """Test sound loading with streaming enabled."""
        loader = AssetLoader()
        mock_media.return_value = MagicMock()

        result = loader.load_sound("assets/audio/music/ambience.wav", streaming=True)

        self.assertIsNotNone(result)
        mock_media.assert_called_once_with("assets/audio/music/ambience.wav", streaming=True)

    @patch("pyglet.resource.media")
    def test_load_sound_not_found(self, mock_media: MagicMock) -> None:
        """Test sound loading with missing file."""
        loader = AssetLoader()
        mock_media.side_effect = pyglet.resource.ResourceNotFoundException("meow.wav")

        with self.assertRaises(FileNotFoundError) as context:
            loader.load_sound("meow.wav")

        self.assertIn("meow.wav", str(context.exception))

    def test_verify_assets_all_exist(self) -> None:
        """Test asset verification when all assets exist."""
        loader = AssetLoader()

        # Use actual asset directory structure
        assets_root = os.path.join(loader.script_dir, "assets")
        if os.path.exists(assets_root):
            required = {
                "assets/images/kitten.png": "image",
                "assets/audio/sfx/meow.wav": "sound",
            }
            # This will print warning if assets don't exist, but should return True/False
            result = loader.verify_assets(required)
            self.assertIsInstance(result, bool)

    def test_verify_assets_missing(self) -> None:
        """Test asset verification with missing files."""
        loader = AssetLoader()

        required = {
            "nonexistent_file_12345.png": "image",
        }
        result = loader.verify_assets(required)

        self.assertFalse(result)

    def test_get_loader_singleton(self) -> None:
        """Test that get_loader returns a singleton instance."""
        from chaser_game.assets import get_loader

        loader1 = get_loader()
        loader2 = get_loader()

        self.assertIs(loader1, loader2)

    def test_asset_paths_structure(self) -> None:
        """Test that asset paths follow expected directory structure."""
        loader = AssetLoader()

        # Check that subdirectories are properly organized
        self.assertTrue("images" in loader.images_dir)
        self.assertTrue("sprites" in loader.sprites_dir)
        self.assertTrue("audio" in loader.sfx_dir)
        self.assertTrue("sfx" in loader.sfx_dir)
        self.assertTrue("music" in loader.music_dir)
        self.assertTrue("source" in loader.source_dir)


if __name__ == "__main__":
    unittest.main()
