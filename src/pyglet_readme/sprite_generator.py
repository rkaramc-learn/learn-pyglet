"""Sprite sheet generation utilities.

Generates sprite sheets from video sources using ffmpeg.
"""

import shutil
import subprocess
from pathlib import Path


class SpriteSheetGenerator:
    """Generates sprite sheets from video files using ffmpeg."""

    def __init__(self) -> None:
        """Initialize the generator and check ffmpeg availability."""
        self.ffmpeg = shutil.which("ffmpeg")
        if not self.ffmpeg:
            raise FileNotFoundError("ffmpeg not found. Install from https://ffmpeg.org/download.html")

    def generate(
        self,
        video_path: str,
        output_path: str,
        grid_width: int = 10,
        grid_height: int = 10,
        frame_width: int = 100,
        frame_height: int = 100,
    ) -> bool:
        """Generate a sprite sheet from a video file.

        Args:
            video_path: Path to input video file.
            output_path: Path to output sprite sheet PNG.
            grid_width: Number of columns in sprite grid.
            grid_height: Number of rows in sprite grid.
            frame_width: Width of each frame in pixels.
            frame_height: Height of each frame in pixels.

        Returns:
            True if generation succeeded, False otherwise.

        Raises:
            FileNotFoundError: If video file doesn't exist.
        """
        video = Path(video_path)
        if not video.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        total_frames = grid_width * grid_height
        fps_filter = "fps=10"  # Reasonable default FPS for sprite extraction
        scale_filter = f"scale={frame_width}:{frame_height}"
        tile_filter = f"tile=layout={grid_width}x{grid_height}"

        cmd = [
            self.ffmpeg,
            "-i",
            str(video),
            "-vf",
            f"{fps_filter},{scale_filter},{tile_filter}",
            "-frames:v",
            "1",
            "-update",
            "1",
            "-y",
            str(output),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running ffmpeg: {e}")
            return False

    @staticmethod
    def get_video_info(video_path: str) -> dict[str, str | float] | None:
        """Get video information using ffprobe.

        Args:
            video_path: Path to video file.

        Returns:
            Dict with duration, fps, and estimated frame count, or None if ffprobe unavailable.
        """
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return None

        try:
            video = Path(video_path)
            if not video.exists():
                return None

            # Get duration
            duration_cmd = [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video),
            ]
            duration_result = subprocess.run(
                duration_cmd, capture_output=True, text=True, check=False
            )
            duration = float(duration_result.stdout.strip())

            # Get FPS
            fps_cmd = [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video),
            ]
            fps_result = subprocess.run(fps_cmd, capture_output=True, text=True, check=False)
            fps_str = fps_result.stdout.strip()
            # Handle fractional fps (e.g., "30000/1001")
            if "/" in fps_str:
                parts = fps_str.split("/")
                fps = float(parts[0]) / float(parts[1])
            else:
                fps = float(fps_str)

            estimated_frames = int(duration * fps)

            return {
                "duration": duration,
                "fps": fps,
                "estimated_frames": estimated_frames,
            }
        except Exception:
            return None
