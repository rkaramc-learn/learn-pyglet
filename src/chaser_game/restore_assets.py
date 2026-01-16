"""Asset restoration CLI for pyglet-readme.

Restores missing gitignored assets by regenerating from sources or downloading
from remote locations. Uses asset manifest for metadata and restoration strategy.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

from .logging_config import TRACE_LEVEL, init_logging


def get_asset_dir() -> Path:
    """Get the assets directory path."""
    return Path(__file__).parent / "assets"


def load_manifest() -> dict[str, Any]:
    """Load asset manifest from YAML file."""
    manifest_path = get_asset_dir() / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Asset manifest not found: {manifest_path}")

    with open(manifest_path) as f:
        return yaml.safe_load(f) or {}


def asset_exists(asset_path: str) -> bool:
    """Check if an asset file exists."""
    full_path = get_asset_dir() / asset_path
    return full_path.exists()


def regenerate_sprite_sheet(logger: logging.Logger, dry_run: bool = False) -> bool:
    """Regenerate mouse_sheet.png from mouse.mp4 using sprite_generator.

    Args:
        logger: Logger instance
        dry_run: If True, only log what would be done

    Returns:
        True if successful or dry_run, False otherwise
    """
    from .sprite_generator import SpriteSheetGenerator

    mouse_video = get_asset_dir() / "source" / "mouse.mp4"
    mouse_sheet = get_asset_dir() / "sprites" / "mouse_sheet.png"

    if not mouse_video.exists():
        logger.error(f"Source video not found: {mouse_video}")
        return False

    if dry_run:
        logger.info(f"[DRY RUN] Would regenerate: {mouse_sheet}")
        return True

    try:
        logger.info(f"Regenerating sprite sheet from {mouse_video}")
        generator = SpriteSheetGenerator()
        generator.generate(str(mouse_video), str(mouse_sheet))
        logger.info(f"Successfully regenerated: {mouse_sheet}")
        return True
    except Exception as e:
        logger.error(f"Failed to regenerate sprite sheet: {e}")
        return False


def download_asset(
    asset_path: str, url: str, logger: logging.Logger, dry_run: bool = False
) -> bool:
    """Download a remote asset.

    Args:
        asset_path: Relative path within assets/
        url: URL to download from
        logger: Logger instance
        dry_run: If True, only log what would be done

    Returns:
        True if successful or dry_run, False otherwise
    """
    full_path = get_asset_dir() / asset_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.info(f"[DRY RUN] Would download: {asset_path} from {url}")
        return True

    try:
        logger.info(f"Downloading {asset_path} from {url}")
        # Use urllib to avoid external dependencies
        import urllib.request

        urllib.request.urlretrieve(url, full_path)
        logger.info(f"Successfully downloaded: {asset_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {asset_path}: {e}")
        return False


def verify_assets(logger: logging.Logger) -> bool:
    """Verify all assets from manifest are present.

    Args:
        logger: Logger instance

    Returns:
        True if all assets present, False if any missing
    """
    manifest = load_manifest()
    all_present = True

    logger.info("Verifying assets...")

    # Check images
    for asset_name, asset_info in manifest.get("images", {}).items():
        path = asset_info.get("path")
        tracked = asset_info.get("tracked", False)
        exists = asset_exists(path)

        status = "[OK]" if exists else "[MISSING]"
        tracked_str = "(tracked)" if tracked else "(gitignored)"
        logger.info(f"  {status} {path} {tracked_str}")

        if not exists and tracked:
            all_present = False

    # Check audio (flat structure: audio.meow, audio.ambience)
    for asset_name, asset_info in manifest.get("audio", {}).items():
        path = asset_info.get("path")
        tracked = asset_info.get("tracked", False)
        exists = asset_exists(path)

        status = "[OK]" if exists else "[MISSING]"
        tracked_str = "(tracked)" if tracked else "(gitignored)"
        logger.info(f"  {status} {path} {tracked_str}")

        if not exists and tracked:
            all_present = False

    # Check source assets
    for asset_name, asset_info in manifest.get("source", {}).items():
        path = asset_info.get("path")
        tracked = asset_info.get("tracked", False)
        exists = asset_exists(path)

        status = "[OK]" if exists else "[MISSING]"
        tracked_str = "(tracked)" if tracked else "(gitignored)"
        logger.info(f"  {status} {path} {tracked_str}")

        if not exists and tracked:
            all_present = False

    if all_present:
        logger.info("All assets verified successfully")
    else:
        logger.warning("Some tracked assets are missing")

    return all_present


def restore_assets(logger: logging.Logger, dry_run: bool = False, confirm: bool = True) -> bool:
    """Restore missing assets.

    Args:
        logger: Logger instance
        dry_run: If True, only log what would be done
        confirm: If True, ask for user confirmation before overwriting/moving

    Returns:
        True if all assets restored or already present, False if any restoration failed
    """
    manifest = load_manifest()
    all_restored = True

    logger.info("Restoring missing assets...")

    # Iterate over all images in manifest
    for asset_name, asset_info in manifest.get("images", {}).items():
        path_str = asset_info.get("path")
        if not path_str:
            continue

        path = get_asset_dir() / path_str

        if path.exists():
            logger.info(f"  [OK] Already present: {path_str}")
            continue

        # Check if we can regenerate this asset
        # Currently hardcoded for mouse_sheet, but logic is generic
        is_regeneratable = asset_name == "mouse_sheet"

        if is_regeneratable:
            if dry_run:
                logger.info(f"  [DRY RUN] Would regenerate: {path_str}")
                continue

            logger.info(f"  [REGENERATING] {path_str}")

            # Generate to temp file first
            import shutil
            import tempfile

            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_path = Path(tmp_file.name)

                # Close file so generator can write to it

                # Call generator with temp path
                # Note: regeneration functions currently take full paths
                # We need to adapt regenerate_sprite_sheet to take output path override or just call generator directly here
                # Re-using existing function structure for specific asset
                if asset_name == "mouse_sheet":
                    # We can't use existing regenerate_sprite_sheet easily as it hardcodes paths
                    # So we inline the logic or modify regenerate_sprite_sheet.
                    # Let's modify regenerate_sprite_sheet signature slightly in a separate tool call if needed,
                    # or just import the generator class here.

                    from .sprite_generator import SpriteSheetGenerator

                    mouse_video = get_asset_dir() / "source" / "mouse.mp4"

                    if not mouse_video.exists():
                        logger.error(f"  [ERROR] Source video missing for {path_str}")
                        all_restored = False
                        continue

                    generator = SpriteSheetGenerator()
                    logger.debug(f"Generating to temp file: {tmp_path}")
                    generator.generate(str(mouse_video), str(tmp_path))

                    # Confirmation
                    if confirm:
                        response = input(f"Asset regenerated at {tmp_path}. Move to {path}? [y/N] ")
                        if response.lower() not in ("y", "yes"):
                            logger.warning("  [SKIPPED] User aborted move.")
                            tmp_path.unlink()  # Cleanup
                            all_restored = False  # Treated as not restored
                            continue

                    # Move to final location
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(tmp_path), str(path))
                    logger.info(f"  [SUCCESS] Restored {path_str}")
                    continue

            except Exception as e:
                logger.error(f"  [ERROR] Failed to regenerate {path_str}: {e}")
                if "tmp_path" in locals() and tmp_path.exists():
                    tmp_path.unlink()
                all_restored = False
                continue

        # If not regeneratable (or regeneration logic skipped), check tracking status
        tracked = asset_info.get("tracked", False)
        if not tracked:
            logger.debug(f"  [SKIP] Gitignored (not required): {path_str}")
            continue

        logger.warning(f"  [ERROR] Missing tracked asset: {path_str}")
        all_restored = False

    # Restore audio (flat structure: audio.meow, audio.ambience)
    # Audio regeneration not implemented yet
    for asset_name, asset_info in manifest.get("audio", {}).items():
        path_str = asset_info.get("path")
        if not path_str:
            continue

        path = get_asset_dir() / path_str
        tracked = asset_info.get("tracked", False)

        if path.exists():
            logger.info(f"  [OK] Already present: {path_str}")
            continue

        if not tracked:
            logger.debug(f"  [SKIP] Gitignored (not required): {path_str}")
            continue

        # For tracked audio assets that are missing, log warning
        logger.warning(f"  [WARN] Missing tracked audio: {path_str}")
        all_restored = False

    if all_restored:
        logger.info("All required assets restored successfully")
    else:
        logger.warning("Some assets could not be restored")

    return all_restored


def verify_command(args: argparse.Namespace) -> int:
    """Handle verify command."""
    logger = logging.getLogger(__name__)

    try:
        all_present = verify_assets(logger)
        return 0 if all_present else 1
    except Exception as e:
        logger.error(f"Verification failed: {e}", exc_info=args.verbose >= 3)
        return 1


def restore_command(args: argparse.Namespace) -> int:
    """Handle restore command."""
    logger = logging.getLogger(__name__)

    try:
        if args.dry_run:
            logger.info("Running in DRY-RUN mode (no changes will be made)")

        # confirm is True unless --yes is passed (args.yes is True -> confirm False? No, confirm=not args.yes)
        # Assuming --yes means "skip confirmation"
        confirm = not args.yes

        all_restored = restore_assets(logger, dry_run=args.dry_run, confirm=confirm)
        return 0 if all_restored else 1
    except Exception as e:
        logger.error(f"Restore failed: {e}", exc_info=args.verbose >= 3)
        return 1


def restore_assets_cli() -> None:
    """CLI entry point for restore-assets command."""
    parser = argparse.ArgumentParser(
        description="Restore missing gitignored assets for pyglet-readme"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify all assets are present")
    verify_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity: -v (INFO), -vv (DEBUG), -vvv (TRACE)",
    )
    verify_parser.set_defaults(func=verify_command)

    # Restore command
    restore_parser = subparsers.add_parser(
        "restore", help="Restore missing assets (regenerate + download)"
    )
    restore_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity: -v (INFO), -vv (DEBUG), -vvv (TRACE)",
    )
    restore_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be restored without making changes",
    )
    restore_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompts (assume yes)",
    )
    restore_parser.set_defaults(func=restore_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Determine log level based on verbosity count
    if args.verbose == 0:
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose == 2:
        log_level = logging.DEBUG
    else:  # 3 or more
        log_level = TRACE_LEVEL

    init_logging(level=log_level, log_file=None)

    exit_code = args.func(args)
    sys.exit(exit_code)
