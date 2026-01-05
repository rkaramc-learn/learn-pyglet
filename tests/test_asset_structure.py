"""Integration tests for asset directory structure and file locations."""

import os
import unittest
from pathlib import Path

from pyglet_readme.asset_manifest import AssetManifest


class TestAssetDirectoryStructure(unittest.TestCase):
    """Tests for asset directory structure and organization."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Get the pyglet_readme package directory
        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        pyglet_readme_dir = os.path.join(project_root, "src", "pyglet_readme")
        self.assets_root = os.path.join(pyglet_readme_dir, "assets")
        self.manifest_path = os.path.join(self.assets_root, "manifest.yaml")

    def test_assets_directory_exists(self) -> None:
        """Test that assets directory exists."""
        self.assertTrue(
            os.path.isdir(self.assets_root),
            f"Assets directory not found: {self.assets_root}",
        )

    def test_required_subdirectories_exist(self) -> None:
        """Test that all required subdirectories exist."""
        required_dirs = [
            "images",
            "sprites",
            "audio",
            "audio/sfx",
            "audio/music",
            "source",
        ]

        for subdir in required_dirs:
            dir_path = os.path.join(self.assets_root, subdir)
            self.assertTrue(
                os.path.isdir(dir_path),
                f"Required subdirectory not found: {dir_path}",
            )

    def test_manifest_file_exists(self) -> None:
        """Test that manifest.yaml exists."""
        self.assertTrue(
            os.path.isfile(self.manifest_path),
            f"Manifest file not found: {self.manifest_path}",
        )

    def test_tracked_assets_exist(self) -> None:
        """Test that all tracked assets exist in their expected locations."""
        manifest = AssetManifest(self.manifest_path)
        tracked = manifest.get_tracked_assets()

        missing = []
        for asset_path in tracked:
            full_path = os.path.join(self.assets_root, asset_path)
            if not os.path.isfile(full_path):
                missing.append(asset_path)

        self.assertEqual(
            len(missing),
            0,
            f"Missing tracked assets: {missing}",
        )

    def test_ignored_assets_directory_structure(self) -> None:
        """Test that ignored asset directories exist even if files don't."""
        # Ignored assets directories should still exist (may be empty due to .gitignore)
        ignored_dirs = [
            "sprites",
            "audio/music",
            "source",
        ]

        for dir_name in ignored_dirs:
            dir_path = os.path.join(self.assets_root, dir_name)
            self.assertTrue(
                os.path.isdir(dir_path),
                f"Ignored asset directory should exist: {dir_path}",
            )

    def test_gitkeep_files_present(self) -> None:
        """Test that .gitkeep files exist to preserve ignored directories."""
        gitkeep_paths = [
            os.path.join(self.assets_root, "sprites", ".gitkeep"),
            os.path.join(self.assets_root, "audio", "music", ".gitkeep"),
        ]

        for gitkeep_path in gitkeep_paths:
            self.assertTrue(
                os.path.isfile(gitkeep_path),
                f".gitkeep file not found: {gitkeep_path}",
            )

    def test_no_assets_in_root_directory(self) -> None:
        """Test that no asset files are directly in the assets root directory."""
        image_extensions = {".png", ".jpg", ".jpeg", ".gif"}
        audio_extensions = {".wav", ".mp3", ".ogg", ".flac"}

        for item in os.listdir(self.assets_root):
            item_path = os.path.join(self.assets_root, item)
            if os.path.isfile(item_path):
                _, ext = os.path.splitext(item)
                self.assertNotIn(
                    ext.lower(),
                    image_extensions | audio_extensions,
                    f"Asset file should not be in root: {item}",
                )

    def test_manifest_asset_paths_structure(self) -> None:
        """Test that manifest asset paths follow expected directory structure."""
        manifest = AssetManifest(self.manifest_path)

        # Check that image assets are in images/ or sprites/
        for asset in manifest.images.values():
            if isinstance(asset, dict):
                path = asset.get("path", "")
                self.assertTrue(
                    "images/" in path or "sprites/" in path,
                    f"Image asset path doesn't follow structure: {path}",
                )

        # Check that audio assets are in audio/sfx/ or audio/music/
        for asset in manifest.audio.values():
            if isinstance(asset, dict):
                path = asset.get("path", "")
                self.assertTrue(
                    "audio/sfx/" in path or "audio/music/" in path,
                    f"Audio asset path doesn't follow structure: {path}",
                )

        # Check that source assets are in source/
        for asset in manifest.source.values():
            if isinstance(asset, dict):
                path = asset.get("path", "")
                self.assertTrue(
                    "source/" in path,
                    f"Source asset path doesn't follow structure: {path}",
                )

    def test_asset_file_permissions_readable(self) -> None:
        """Test that tracked asset files are readable."""
        manifest = AssetManifest(self.manifest_path)
        tracked = manifest.get_tracked_assets()

        for asset_path in tracked:
            full_path = os.path.join(self.assets_root, asset_path)
            if os.path.isfile(full_path):
                self.assertTrue(
                    os.access(full_path, os.R_OK),
                    f"Asset file not readable: {full_path}",
                )

    def test_no_duplicate_asset_paths(self) -> None:
        """Test that no asset paths are duplicated in manifest."""
        manifest = AssetManifest(self.manifest_path)
        paths = manifest.get_asset_paths()

        duplicates = [p for p in paths if paths.count(p) > 1]
        self.assertEqual(
            len(duplicates),
            0,
            f"Duplicate asset paths found: {set(duplicates)}",
        )

    def test_subdirectory_organization_consistency(self) -> None:
        """Test that subdirectories are organized consistently."""
        # images directory should contain image files
        images_dir = os.path.join(self.assets_root, "images")
        if os.path.isdir(images_dir):
            for item in os.listdir(images_dir):
                if os.path.isfile(os.path.join(images_dir, item)):
                    _, ext = os.path.splitext(item)
                    self.assertIn(
                        ext.lower(),
                        {".png", ".jpg", ".jpeg", ".gif", ""},
                        f"Non-image file in images dir: {item}",
                    )

        # sfx directory should contain audio files
        sfx_dir = os.path.join(self.assets_root, "audio", "sfx")
        if os.path.isdir(sfx_dir):
            for item in os.listdir(sfx_dir):
                if os.path.isfile(os.path.join(sfx_dir, item)):
                    _, ext = os.path.splitext(item)
                    self.assertIn(
                        ext.lower(),
                        {".wav", ".mp3", ".ogg", ".flac", ""},
                        f"Non-audio file in sfx dir: {item}",
                    )

    def test_manifest_lists_all_tracked_assets(self) -> None:
        """Test that all tracked asset files are listed in manifest."""
        manifest = AssetManifest(self.manifest_path)
        manifest_paths = set(manifest.get_asset_paths())

        # Scan actual directories for tracked assets
        tracked_asset_extensions = {".png", ".wav"}
        actual_files = set()

        for root, dirs, files in os.walk(self.assets_root):
            # Skip ignored directories
            if ".gitkeep" in root or root == os.path.join(self.assets_root, "source"):
                continue

            for file in files:
                if file == ".gitkeep":
                    continue

                _, ext = os.path.splitext(file)
                if ext.lower() in tracked_asset_extensions:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.assets_root)
                    # Normalize path separators for cross-platform compatibility
                    rel_path = rel_path.replace(os.sep, "/")
                    actual_files.add(rel_path)

        # Check that manifest includes actual tracked assets
        for actual_file in actual_files:
            # Some tracked assets might be in ignored directories
            if "music" not in actual_file and "source" not in actual_file:
                self.assertIn(
                    actual_file,
                    manifest_paths,
                    f"Tracked asset not in manifest: {actual_file}",
                )


class TestAssetPathConsistency(unittest.TestCase):
    """Tests for consistency of asset paths across the system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        pyglet_readme_dir = os.path.join(project_root, "src", "pyglet_readme")
        self.assets_root = os.path.join(pyglet_readme_dir, "assets")
        self.manifest_path = os.path.join(self.assets_root, "manifest.yaml")

    def test_asset_paths_use_forward_slashes(self) -> None:
        """Test that all asset paths in manifest use forward slashes."""
        manifest = AssetManifest(self.manifest_path)
        paths = manifest.get_asset_paths()

        for path in paths:
            self.assertNotIn(
                "\\",
                path,
                f"Asset path uses backslashes (should use /): {path}",
            )
            self.assertIn(
                "/",
                path,
                f"Asset path doesn't include directory separator: {path}",
            )

    def test_asset_paths_follow_structure(self) -> None:
        """Test that all asset paths follow expected structure."""
        manifest = AssetManifest(self.manifest_path)
        paths = manifest.get_asset_paths()

        for path in paths:
            # Paths should have directory structure (images/, sprites/, audio/, source/)
            self.assertIn(
                "/",
                path,
                f"Asset path missing directory structure: {path}",
            )

    def test_asset_extensions_valid(self) -> None:
        """Test that assets have valid file extensions."""
        manifest = AssetManifest(self.manifest_path)
        paths = manifest.get_asset_paths()

        valid_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".wav",
            ".mp3",
            ".ogg",
            ".flac",
            ".mp4",
        }

        for path in paths:
            _, ext = os.path.splitext(path)
            self.assertIn(
                ext.lower(),
                valid_extensions,
                f"Asset has invalid extension: {path}",
            )


if __name__ == "__main__":
    unittest.main()
