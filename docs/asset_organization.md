# Asset Organization

This document outlines the organization, tracking, and management of assets in the `chaser-game` project.

## Directory Structure

Assets are located in `src/chaser_game/assets/`.

```text
src/chaser_game/assets/
├── manifest.yaml       # Source of truth for all assets
├── images/             # Static images (sprites, UI)
│   ├── kitten.png
│   └── chaser_logo.png
├── sprites/            # Animated sprite sheets
│   └── mouse_sheet.png # Generated from source video
├── audio/              # Sound effects and music
│   ├── sfx/meow.wav
│   └── music/ambience.wav
└── source/             # Source files for generation
    ├── mouse.mp4       # Source for mouse_sheet.png
    └── chaser_logo.svg # Source for chaser_logo.png
```

## Manifest Schema

The `manifest.yaml` file defines metadata for all assets. It controls verification and restoration logic.

### Fields

- **path**: Relative path to the asset file.
- **type**: Asset category (e.g., `sprite`, `sound_effect`, `video_source`).
- **tracked**: `true` if committed to git, `false` if gitignored (generated/downloaded).
- **verify**: _Optional_. Block defining strict integrity checks.

### Verification Block

Assets with a `verify` block are validated by their content hash and metadata.

```yaml
mouse_sheet:
  verify:
    sha256: "A8D2..." # SHA256 content hash
    dimensions: [2280, 1280] # [Width, Height] in pixels
    format: "PNG" # File format
```

**Audio Assets** support additional fields:

```yaml
meow:
  verify:
    sha256: "81C7..."
    duration_seconds: 0.88 # Expected duration (±0.1s tolerance)
    channels: 2 # Channel count
    sample_rate: 44100 # Sample rate in Hz
```

## Asset Lifecycle

### 1. Tracked Assets

Assets marked `tracked: true` are committed to the repository.

- **Integrity**: Verified using SHA256 hashes in `manifest.yaml`.
- **Examples**: `kitten.png`, `chaser_logo.png`, `meow.wav`.

### 2. Generated/Ignored Assets

Assets marked `tracked: false` are **not** committed (gitignored). They must be restored (regenerated or downloaded) on a fresh checkout.

- **Restoration**: The `restore_assets.py` script handles generation.
- **Example**: `mouse_sheet.png`.
  - **Source**: `source/mouse.mp4`.
  - **Method**: Generated via `ffmpeg` frame extraction.

### 3. Source Assets

Raw files used to generate other assets.

- **Example**: `mouse.mp4` (Ignored, local source), `chaser_logo.svg` (Tracked).

## CLI Tools

The main CLI provides commands to manage assets.

### Verification

Verify presence and integrity of all tracked assets.

```bash
uv run chaser assets verify [-v]
```

- Checks existence of all assets in manifest.
- Validates SHA256 hash and metadata for assets with a `verify` block.

### Restoration

Restore missing or corrupted assets.

```bash
uv run chaser assets restore [--dry-run] [--yes]
```

- Regenerates missing ignores assets (e.g. `mouse_sheet.png`).
- Checks for interactive confirmation unless `--yes` is used.
- Safe regeneration: Generates to a temporary file first, then moves it to the target location upon success/confirmation.
