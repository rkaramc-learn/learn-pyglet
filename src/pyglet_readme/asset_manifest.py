"""Asset manifest parser and validator.

Loads and validates asset metadata from assets/manifest.yaml.
"""

import os
from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class AssetMetadata:
    """Metadata for a single asset."""

    name: str
    path: str
    asset_type: str
    tracked: bool
    description: str
    dimensions: tuple[int, int] | None = None
    format: str | None = None


class AssetManifest:
    """Parses and validates asset manifest."""

    def __init__(self, manifest_path: str) -> None:
        """Load and parse the asset manifest.

        Args:
            manifest_path: Path to manifest.yaml file.

        Raises:
            FileNotFoundError: If manifest file doesn't exist.
            yaml.YAMLError: If manifest is invalid YAML.
        """
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            self.data: dict[str, Any] = yaml.safe_load(f) or {}

        self.version: str = self.data.get("version", "unknown")
        self.images: dict[str, Any] = self.data.get("images", {})
        self.audio: dict[str, Any] = self.data.get("audio", {})
        self.source: dict[str, Any] = self.data.get("source", {})

    def get_asset_paths(self) -> list[str]:
        """Get all asset paths from manifest.

        Returns:
            List of relative asset paths.
        """
        paths = []
        for asset in self.images.values():
            if isinstance(asset, dict):
                paths.append(asset.get("path", ""))
        for asset in self.audio.values():
            if isinstance(asset, dict):
                paths.append(asset.get("path", ""))
        for asset in self.source.values():
            if isinstance(asset, dict):
                paths.append(asset.get("path", ""))
        return [p for p in paths if p]

    def get_tracked_assets(self) -> list[str]:
        """Get paths of all tracked assets.

        Returns:
            List of tracked asset paths.
        """
        tracked = []
        for asset in self.images.values():
            if isinstance(asset, dict) and asset.get("tracked"):
                tracked.append(asset.get("path", ""))
        for asset in self.audio.values():
            if isinstance(asset, dict) and asset.get("tracked"):
                tracked.append(asset.get("path", ""))
        for asset in self.source.values():
            if isinstance(asset, dict) and asset.get("tracked"):
                tracked.append(asset.get("path", ""))
        return [p for p in tracked if p]

    def get_ignored_assets(self) -> list[str]:
        """Get paths of all ignored assets.

        Returns:
            List of ignored asset paths.
        """
        ignored = []
        for asset in self.images.values():
            if isinstance(asset, dict) and not asset.get("tracked"):
                ignored.append(asset.get("path", ""))
        for asset in self.audio.values():
            if isinstance(asset, dict) and not asset.get("tracked"):
                ignored.append(asset.get("path", ""))
        for asset in self.source.values():
            if isinstance(asset, dict) and not asset.get("tracked"):
                ignored.append(asset.get("path", ""))
        return [p for p in ignored if p]

    def validate_assets(self, assets_root: str) -> tuple[bool, list[str]]:
        """Validate that all tracked assets exist on disk.

        Args:
            assets_root: Root directory containing assets.

        Returns:
            Tuple of (all_valid, list_of_missing_paths).
        """
        missing = []
        for path in self.get_tracked_assets():
            full_path = os.path.join(assets_root, path)
            if not os.path.exists(full_path):
                missing.append(path)

        return len(missing) == 0, missing
