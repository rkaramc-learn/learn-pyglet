"""Integration tests for sprite sheet generation workflow via restore_assets CLI.

Tests the end-to-end workflow of regenerating sprite sheets from video sources
using the restore-assets CLI and sprite_generator module.
"""

import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from chaser_game.restore_assets import regenerate_sprite_sheet, restore_assets
from chaser_game.sprite_generator import SpriteSheetGenerator


class TestSpriteGenerationWorkflow(unittest.TestCase):
    """Integration tests for sprite sheet generation workflow."""

    def setUp(self) -> None:
        """Set up test environment with temporary directories."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_assets_dir = Path(self.temp_dir.name) / "assets"
        self.test_assets_dir.mkdir(parents=True, exist_ok=True)

        # Create asset subdirectories
        (self.test_assets_dir / "source").mkdir(exist_ok=True)
        (self.test_assets_dir / "sprites").mkdir(exist_ok=True)

        # Create test video file
        self.test_video = self.test_assets_dir / "source" / "mouse.mp4"
        self.test_video.touch()

        # Expected output
        self.expected_sprite_sheet = self.test_assets_dir / "sprites" / "mouse_sheet.png"

        # Set up logger
        self.logger = logging.getLogger(__name__)

    def tearDown(self) -> None:
        """Clean up temporary directories."""
        self.temp_dir.cleanup()

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_regenerate_sprite_sheet_success(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test successful sprite sheet regeneration via restore_assets."""
        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        # Simulate successful generation by creating output file
        def run_side_effect(*args: tuple, **kwargs):  # type: ignore
            self.expected_sprite_sheet.touch()
            result = MagicMock()
            result.returncode = 0
            return result

        mock_run.side_effect = run_side_effect

        result = regenerate_sprite_sheet(self.logger, dry_run=False)

        self.assertTrue(result)
        self.assertTrue(self.expected_sprite_sheet.exists())

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("shutil.which")
    def test_regenerate_sprite_sheet_missing_video(
        self,
        mock_which: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test regeneration fails gracefully when video source is missing."""
        # Create assets dir without the source video
        empty_assets_dir = Path(self.temp_dir.name) / "empty_assets"
        empty_assets_dir.mkdir()
        (empty_assets_dir / "source").mkdir()
        (empty_assets_dir / "sprites").mkdir()

        mock_get_asset_dir.return_value = empty_assets_dir
        mock_which.return_value = "ffmpeg"

        result = regenerate_sprite_sheet(self.logger, dry_run=False)

        self.assertFalse(result)

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("shutil.which")
    def test_regenerate_sprite_sheet_ffmpeg_not_available(
        self,
        mock_which: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test regeneration fails when ffmpeg is not available."""
        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = None

        result = regenerate_sprite_sheet(self.logger, dry_run=False)

        self.assertFalse(result)

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("shutil.which")
    def test_regenerate_sprite_sheet_dry_run(
        self,
        mock_which: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test dry-run mode logs without generating sprite sheet."""
        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = "ffmpeg"

        result = regenerate_sprite_sheet(self.logger, dry_run=True)

        self.assertTrue(result)
        self.assertFalse(self.expected_sprite_sheet.exists())

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_sprite_generator_receives_correct_paths(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test that SpriteSheetGenerator receives correct video and output paths."""
        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = "ffmpeg"

        call_captured = []

        def run_side_effect(*args: tuple, **kwargs):  # type: ignore
            call_captured.append(args[0])
            self.expected_sprite_sheet.touch()
            result = MagicMock()
            result.returncode = 0
            return result

        mock_run.side_effect = run_side_effect

        result = regenerate_sprite_sheet(self.logger, dry_run=False)

        self.assertTrue(result)
        self.assertEqual(len(call_captured), 1)
        cmd = call_captured[0]

        # Verify command structure contains correct paths
        self.assertIn(str(self.test_video), cmd)
        self.assertIn(str(self.expected_sprite_sheet), cmd)
        self.assertIn("-i", cmd)  # input flag
        self.assertIn("ffmpeg", cmd[0])

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("chaser_game.restore_assets.load_manifest")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_restore_assets_regenerates_missing_sprite_sheet(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
        mock_load_manifest: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test restore_assets workflow detects and regenerates missing sprite sheets."""
        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        # Mock manifest indicating sprite sheet should exist
        mock_load_manifest.return_value = {
            "images": {
                "kitten": {"path": "sprites/kitten.png", "tracked": True},
                "mouse_sheet": {
                    "path": "sprites/mouse_sheet.png",
                    "tracked": False,
                    "source": "source/mouse.mp4",
                },
            },
            "audio": {"sfx": {}, "music": {}},
        }

        # Simulate sprite sheet creation
        def run_side_effect(*args: tuple, **kwargs):  # type: ignore
            self.expected_sprite_sheet.touch()
            result = MagicMock()
            result.returncode = 0
            return result

        mock_run.side_effect = run_side_effect

        # Verify sprite sheet doesn't exist initially
        self.assertFalse(self.expected_sprite_sheet.exists())

        # Run restore
        result = restore_assets(self.logger, dry_run=False)

        # Sprite sheet should now exist
        self.assertTrue(self.expected_sprite_sheet.exists())

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("chaser_game.restore_assets.load_manifest")
    def test_restore_assets_preserves_existing_sprite_sheets(
        self,
        mock_load_manifest: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test restore_assets doesn't overwrite existing sprite sheets."""
        mock_get_asset_dir.return_value = self.test_assets_dir

        # Create an existing sprite sheet with original content
        original_content = b"original sprite sheet data"
        self.expected_sprite_sheet.touch()
        self.expected_sprite_sheet.write_bytes(original_content)

        mock_load_manifest.return_value = {
            "images": {
                "mouse_sheet": {
                    "path": "sprites/mouse_sheet.png",
                    "tracked": False,
                },
            },
            "audio": {"sfx": {}, "music": {}},
        }

        result = restore_assets(self.logger, dry_run=False)

        # Verify original content is preserved
        self.assertTrue(self.expected_sprite_sheet.exists())
        self.assertEqual(self.expected_sprite_sheet.read_bytes(), original_content)

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("chaser_game.restore_assets.load_manifest")
    @patch("shutil.which")
    def test_restore_assets_dry_run_mode(
        self,
        mock_which: MagicMock,
        mock_load_manifest: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test restore_assets dry-run mode doesn't modify files."""
        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = "ffmpeg"

        mock_load_manifest.return_value = {
            "images": {
                "mouse_sheet": {
                    "path": "sprites/mouse_sheet.png",
                    "tracked": False,
                },
            },
            "audio": {"sfx": {}, "music": {}},
        }

        result = restore_assets(self.logger, dry_run=True)

        # Sprite sheet should not be created
        self.assertFalse(self.expected_sprite_sheet.exists())

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_sprite_sheet_output_directory_creation(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test that sprite sheet output directory is created if missing."""
        # Use nested directory structure
        nested_output_dir = (
            self.test_assets_dir / "nested" / "sprite" / "output" / "mouse_sheet.png"
        )

        mock_get_asset_dir.return_value = self.test_assets_dir
        mock_which.return_value = "ffmpeg"

        def run_side_effect(*args: tuple, **kwargs):  # type: ignore
            result = MagicMock()
            result.returncode = 0
            return result

        mock_run.side_effect = run_side_effect

        # Verify parent directory doesn't exist
        self.assertFalse(nested_output_dir.parent.exists())

        # Generate sprite sheet (use SpriteSheetGenerator directly)
        generator = SpriteSheetGenerator()
        generator.generate(str(self.test_video), str(nested_output_dir))

        # Verify parent directory was created
        self.assertTrue(nested_output_dir.parent.exists())


class TestSpriteGenerationCLIWorkflow(unittest.TestCase):
    """Test sprite sheet generation via CLI entry point."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.logger = logging.getLogger(__name__)

    def tearDown(self) -> None:
        """Clean up."""
        self.temp_dir.cleanup()

    @patch("chaser_game.restore_assets.get_asset_dir")
    @patch("chaser_game.restore_assets.load_manifest")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_sprite_generation_with_various_grid_sizes(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
        mock_load_manifest: MagicMock,
        mock_get_asset_dir: MagicMock,
    ) -> None:
        """Test sprite sheet generation respects custom grid dimensions."""
        test_assets_dir = Path(self.temp_dir.name)
        (test_assets_dir / "source").mkdir()
        (test_assets_dir / "sprites").mkdir()
        test_video = test_assets_dir / "source" / "mouse.mp4"
        test_video.touch()

        mock_get_asset_dir.return_value = test_assets_dir
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)
        mock_load_manifest.return_value = {"images": {}, "audio": {"sfx": {}, "music": {}}}

        # Test with custom grid
        generator = SpriteSheetGenerator()
        result = generator.generate(
            str(test_video),
            str(test_assets_dir / "sprites" / "custom_grid.png"),
            grid_width=8,
            grid_height=5,
            frame_width=128,
            frame_height=128,
        )

        self.assertTrue(result)
        call_args = mock_run.call_args
        cmd = " ".join(call_args[0][0])

        # Verify custom parameters in ffmpeg command
        self.assertIn("scale=128:128", cmd)
        self.assertIn("tile=", cmd)


if __name__ == "__main__":
    unittest.main()
