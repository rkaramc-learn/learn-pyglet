"""Unit tests for SpriteSheetGenerator class."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from chaser_game.sprite_generator import SpriteSheetGenerator


class TestSpriteSheetGeneratorInit(unittest.TestCase):
    """Tests for SpriteSheetGenerator initialization."""

    @patch("shutil.which")
    def test_initialization_with_ffmpeg(self, mock_which: MagicMock) -> None:
        """Test initialization when ffmpeg is available."""
        mock_which.return_value = "/usr/bin/ffmpeg"

        generator = SpriteSheetGenerator()

        self.assertIsNotNone(generator.ffmpeg)
        self.assertEqual(generator.ffmpeg, "/usr/bin/ffmpeg")
        mock_which.assert_called_with("ffmpeg")

    @patch("shutil.which")
    def test_initialization_without_ffmpeg(self, mock_which: MagicMock) -> None:
        """Test initialization when ffmpeg is not available."""
        mock_which.return_value = None

        with self.assertRaises(FileNotFoundError) as context:
            SpriteSheetGenerator()

        self.assertIn("ffmpeg", str(context.exception))


class TestSpriteSheetGeneratorGenerate(unittest.TestCase):
    """Tests for sprite sheet generation."""

    def setUp(self) -> None:
        """Create temporary test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_video = os.path.join(self.temp_dir.name, "test.mp4")
        self.test_output = os.path.join(self.temp_dir.name, "output", "sheet.png")

        # Create a dummy video file
        Path(self.test_video).touch()

    def tearDown(self) -> None:
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_generate_success(self, mock_run: MagicMock, mock_which: MagicMock) -> None:
        """Test successful sprite sheet generation."""
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        generator = SpriteSheetGenerator()
        # generate() returns None on success (no exception raised)
        generator.generate(
            self.test_video,
            self.test_output,
            grid_width=10,
            grid_height=10,
            frame_width=100,
            frame_height=100,
        )

        mock_run.assert_called_once()

        # Check command structure
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        self.assertIn("ffmpeg", cmd[0])
        self.assertIn(self.test_video, cmd)
        self.assertIn(self.test_output, cmd)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_generate_failure(self, mock_run: MagicMock, mock_which: MagicMock) -> None:
        """Test sprite sheet generation failure raises CalledProcessError."""
        mock_which.return_value = "ffmpeg"
        # With check=True, non-zero returncode raises CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg", stderr="Error")

        generator = SpriteSheetGenerator()
        with self.assertRaises(subprocess.CalledProcessError):
            generator.generate(self.test_video, self.test_output)

    @patch("shutil.which")
    def test_generate_video_not_found(self, mock_which: MagicMock) -> None:
        """Test generation with missing video file."""
        mock_which.return_value = "ffmpeg"

        generator = SpriteSheetGenerator()

        with self.assertRaises(FileNotFoundError):
            generator.generate(
                "/nonexistent/video.mp4",
                self.test_output,
            )

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_generate_creates_output_directory(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that output directory is created if it doesn't exist."""
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        output_dir = os.path.join(self.temp_dir.name, "new", "path", "sheet.png")
        self.assertFalse(os.path.exists(os.path.dirname(output_dir)))

        generator = SpriteSheetGenerator()
        generator.generate(self.test_video, output_dir)

        # Directory should be created
        self.assertTrue(os.path.exists(os.path.dirname(output_dir)))

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_generate_custom_grid_and_frame_size(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test generation with custom grid and frame dimensions."""
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        generator = SpriteSheetGenerator()
        generator.generate(
            self.test_video,
            self.test_output,
            grid_width=5,
            grid_height=8,
            frame_width=64,
            frame_height=64,
        )

        # Check that custom parameters are in command
        call_args = mock_run.call_args
        cmd = " ".join(call_args[0][0])
        self.assertIn("fps=n=40", cmd)  # 5 * 8 = 40 frames
        self.assertIn("scale=64:64", cmd)
        self.assertIn("tile=5:8", cmd)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_generate_subprocess_exception(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test handling of subprocess exceptions (bubbles up to caller)."""
        mock_which.return_value = "ffmpeg"
        mock_run.side_effect = OSError("Subprocess error")

        generator = SpriteSheetGenerator()
        with self.assertRaises(OSError):
            generator.generate(self.test_video, self.test_output)


class TestSpriteSheetGeneratorVideoInfo(unittest.TestCase):
    """Tests for video info extraction."""

    def setUp(self) -> None:
        """Create temporary test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_video = os.path.join(self.temp_dir.name, "test.mp4")
        Path(self.test_video).touch()

    def tearDown(self) -> None:
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_video_info_success(self, mock_run: MagicMock, mock_which: MagicMock) -> None:
        """Test successful video info extraction."""
        mock_which.side_effect = lambda cmd: ("ffprobe" if cmd == "ffprobe" else None)

        call_count = [0]

        # Mock subprocess calls for duration and fps
        def run_side_effect(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            # First call is duration, second is fps
            if call_count[0] == 0:
                result.stdout = "10.5"
            else:
                result.stdout = "30/1"
            call_count[0] += 1
            return result

        mock_run.side_effect = run_side_effect

        info = SpriteSheetGenerator.get_video_info(self.test_video)

        self.assertIsNotNone(info)
        assert info is not None  # Type guard for pyright
        self.assertIn("duration", info)
        self.assertIn("fps", info)
        self.assertIn("estimated_frames", info)

    @patch("shutil.which")
    def test_get_video_info_no_ffprobe(self, mock_which: MagicMock) -> None:
        """Test video info extraction when ffprobe is unavailable."""
        mock_which.return_value = None

        info = SpriteSheetGenerator.get_video_info(self.test_video)

        self.assertIsNone(info)

    @patch("shutil.which")
    def test_get_video_info_file_not_found(self, mock_which: MagicMock) -> None:
        """Test video info extraction with missing file."""
        mock_which.return_value = "ffprobe"

        info = SpriteSheetGenerator.get_video_info("/nonexistent/video.mp4")

        self.assertIsNone(info)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_video_info_fractional_fps(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test video info with fractional fps (e.g., 30000/1001)."""
        mock_which.return_value = "ffprobe"

        call_count = [0]

        def run_side_effect(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            # First call is duration, second is fps
            if call_count[0] == 0:
                result.stdout = "10.0"
            else:
                result.stdout = "30000/1001"  # NTSC frame rate
            call_count[0] += 1
            return result

        mock_run.side_effect = run_side_effect

        info = SpriteSheetGenerator.get_video_info(self.test_video)

        self.assertIsNotNone(info)
        assert info is not None  # Type guard for pyright
        # 30000/1001 ≈ 29.97
        fps_value = info.get("fps")
        self.assertIsNotNone(fps_value)
        assert isinstance(fps_value, (int, float))
        self.assertAlmostEqual(fps_value, 29.97, places=1)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_video_info_subprocess_exception(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test handling of subprocess exceptions during video info."""
        mock_which.return_value = "ffprobe"
        mock_run.side_effect = Exception("ffprobe error")

        info = SpriteSheetGenerator.get_video_info(self.test_video)

        self.assertIsNone(info)


class TestSpriteSheetGeneratorIntegration(unittest.TestCase):
    """Integration tests for SpriteSheetGenerator."""

    def setUp(self) -> None:
        """Create temporary test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    @patch("shutil.which")
    def test_ffmpeg_availability_check(self, mock_which: MagicMock) -> None:
        """Test that generator properly checks for ffmpeg."""
        mock_which.return_value = "ffmpeg"

        generator = SpriteSheetGenerator()
        self.assertIsNotNone(generator.ffmpeg)

    @patch("shutil.which")
    def test_multiple_generator_instances(self, mock_which: MagicMock) -> None:
        """Test creating multiple generator instances."""
        mock_which.return_value = "ffmpeg"

        gen1 = SpriteSheetGenerator()
        gen2 = SpriteSheetGenerator()

        self.assertEqual(gen1.ffmpeg, gen2.ffmpeg)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_generate_with_default_parameters(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test generation with default grid and frame parameters."""
        mock_which.return_value = "ffmpeg"
        mock_run.return_value = MagicMock(returncode=0)

        temp_video = os.path.join(self.temp_dir.name, "test.mp4")
        temp_output = os.path.join(self.temp_dir.name, "sheet.png")
        Path(temp_video).touch()

        generator = SpriteSheetGenerator()
        # generate() returns None on success
        generator.generate(temp_video, temp_output)

        # Check that defaults were applied (10x10 grid, 100x100 frames)
        call_args = mock_run.call_args
        cmd = " ".join(call_args[0][0])
        self.assertIn("fps=n=100", cmd)  # 10 * 10 = 100
        self.assertIn("scale=100:100", cmd)
        self.assertIn("tile=10:10", cmd)


if __name__ == "__main__":
    unittest.main()
