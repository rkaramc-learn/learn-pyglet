"""Asset management module for pyglet-readme.

Centralizes asset loading with error handling and fallbacks for missing resources.
"""

import logging
import os
import time
from typing import Optional

import pyglet

logger = logging.getLogger(__name__)


class AssetLoader:
    """Manages loading of game assets (images and sounds) with error handling."""

    def __init__(self) -> None:
        """Initialize the asset loader with the assets directory."""
        logger.debug("Initializing AssetLoader")
        self.script_dir = os.path.dirname(__file__)
        self.assets_dir = os.path.join(self.script_dir, "assets")
        self.images_dir = os.path.join(self.assets_dir, "images")
        self.sprites_dir = os.path.join(self.assets_dir, "sprites")
        self.sfx_dir = os.path.join(self.assets_dir, "audio", "sfx")
        self.music_dir = os.path.join(self.assets_dir, "audio", "music")
        self.source_dir = os.path.join(self.assets_dir, "source")

        logger.debug(f"Assets directory: {self.assets_dir}")
        logger.debug(f"Images directory: {self.images_dir}")
        logger.debug(f"Sprites directory: {self.sprites_dir}")
        logger.debug(f"SFX directory: {self.sfx_dir}")
        logger.debug(f"Music directory: {self.music_dir}")
        logger.debug(f"Source directory: {self.source_dir}")

        pyglet.resource.path = [self.script_dir, self.assets_dir]
        pyglet.resource.reindex()
        logger.info("AssetLoader initialized successfully")

    def load_image(self, filename: str) -> pyglet.image.AbstractImage:
        """Load an image asset.

        Args:
            filename: Name of the image file (relative to script directory).

        Returns:
            The loaded image.

        Raises:
            FileNotFoundError: If the asset file is not found.
        """
        logger.debug(f"Loading image: {filename}")
        start_time = time.time()
        try:
            image = pyglet.resource.image(filename)
            elapsed = time.time() - start_time
            logger.debug(
                f"Image loaded successfully in {elapsed:.3f}s: {filename} ({image.width}x{image.height})"
            )
            return image
        except pyglet.resource.ResourceNotFoundException as e:
            logger.error(f"Image asset not found: {filename}")
            raise FileNotFoundError(f"Image asset not found: {filename}") from e

    def load_sound(self, filename: str, streaming: bool = False) -> pyglet.media.Source:
        """Load a sound asset.

        Args:
            filename: Name of the sound file (relative to script directory).
            streaming: Whether to stream the audio (for large files).

        Returns:
            The loaded sound source.

        Raises:
            FileNotFoundError: If the asset file is not found.
        """
        logger.debug(f"Loading sound: {filename} (streaming={streaming})")
        start_time = time.time()
        try:
            sound = pyglet.resource.media(filename, streaming=streaming)
            elapsed = time.time() - start_time
            logger.debug(f"Sound loaded successfully in {elapsed:.3f}s: {filename}")
            return sound
        except pyglet.resource.ResourceNotFoundException as e:
            logger.error(f"Sound asset not found: {filename}")
            raise FileNotFoundError(f"Sound asset not found: {filename}") from e

    def verify_assets(self, required_assets: dict[str, str]) -> bool:
        """Verify that all required assets exist.

        Args:
            required_assets: Dict mapping asset names to types ('image' or 'sound').

        Returns:
            True if all assets exist, False otherwise.
        """
        logger.debug(f"Verifying {len(required_assets)} required assets")
        missing = []
        for asset_name, asset_type in required_assets.items():
            asset_path = os.path.join(self.script_dir, asset_name)
            if not os.path.exists(asset_path):
                missing.append(f"{asset_name} ({asset_type})")
                logger.warning(f"Missing asset: {asset_name} ({asset_type})")
            else:
                logger.debug(f"Found asset: {asset_name}")

        if missing:
            logger.warning(f"Missing assets: {', '.join(missing)}")
            return False
        logger.info(f"All {len(required_assets)} required assets verified")
        return True


# Global asset loader instance
_loader: Optional[AssetLoader] = None


def get_loader() -> AssetLoader:
    """Get or create the global asset loader instance."""
    global _loader
    if _loader is None:
        _loader = AssetLoader()
    return _loader
