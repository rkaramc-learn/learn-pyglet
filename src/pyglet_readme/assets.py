"""Asset management module for pyglet-readme.

Centralizes asset loading with error handling and fallbacks for missing resources.
"""

import os
from typing import Optional

import pyglet


class AssetLoader:
    """Manages loading of game assets (images and sounds) with error handling."""

    def __init__(self) -> None:
        """Initialize the asset loader with the assets directory."""
        self.script_dir = os.path.dirname(__file__)
        self.assets_dir = os.path.join(self.script_dir, "assets")
        self.images_dir = os.path.join(self.assets_dir, "images")
        self.sprites_dir = os.path.join(self.assets_dir, "sprites")
        self.sfx_dir = os.path.join(self.assets_dir, "audio", "sfx")
        self.music_dir = os.path.join(self.assets_dir, "audio", "music")
        self.source_dir = os.path.join(self.assets_dir, "source")
        
        pyglet.resource.path = [self.script_dir, self.assets_dir]
        pyglet.resource.reindex()

    def load_image(self, filename: str) -> pyglet.image.AbstractImage:
        """Load an image asset.

        Args:
            filename: Name of the image file (relative to script directory).

        Returns:
            The loaded image.

        Raises:
            FileNotFoundError: If the asset file is not found.
        """
        try:
            return pyglet.resource.image(filename)
        except pyglet.resource.ResourceNotFoundException as e:
            raise FileNotFoundError(f"Image asset not found: {filename}") from e

    def load_sound(
        self, filename: str, streaming: bool = False
    ) -> pyglet.media.Source:
        """Load a sound asset.

        Args:
            filename: Name of the sound file (relative to script directory).
            streaming: Whether to stream the audio (for large files).

        Returns:
            The loaded sound source.

        Raises:
            FileNotFoundError: If the asset file is not found.
        """
        try:
            return pyglet.resource.media(filename, streaming=streaming)
        except pyglet.resource.ResourceNotFoundException as e:
            raise FileNotFoundError(f"Sound asset not found: {filename}") from e

    def verify_assets(self, required_assets: dict[str, str]) -> bool:
        """Verify that all required assets exist.

        Args:
            required_assets: Dict mapping asset names to types ('image' or 'sound').

        Returns:
            True if all assets exist, False otherwise.
        """
        missing = []
        for asset_name, asset_type in required_assets.items():
            asset_path = os.path.join(self.script_dir, asset_name)
            if not os.path.exists(asset_path):
                missing.append(f"{asset_name} ({asset_type})")

        if missing:
            print(f"Warning: Missing assets: {', '.join(missing)}")
            return False
        return True


# Global asset loader instance
_loader: Optional[AssetLoader] = None


def get_loader() -> AssetLoader:
    """Get or create the global asset loader instance."""
    global _loader
    if _loader is None:
        _loader = AssetLoader()
    return _loader
