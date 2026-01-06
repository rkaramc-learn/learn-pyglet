# Asset Management Guide

This document details all game assets, their sources, generation strategies, and version control policies.

## Asset Inventory

| Asset           | Path                       | Type                   | Size    | Tracked | Source/Generation          | Status         |
| --------------- | -------------------------- | ---------------------- | ------- | ------- | -------------------------- | -------------- |
| **kitten**      | `images/kitten.png`        | Sprite (PNG)           | 0.85 MB | ✅ Yes | Committed directly         | ✅ Checked in |
| **meow**        | `audio/sfx/meow.wav`       | SFX (WAV)              | 0.15 MB | ✅ Yes | Committed directly         | ✅ Checked in |
| **mouse_sheet** | `sprites/mouse_sheet.png`  | Sprite Sheet (PNG)     | 0.95 MB | ❌ No  | Generated from `mouse.mp4` | !!TODO Check in to repository!!            |
| **ambience**    | `audio/music/ambience.wav` | Background Music (WAV) | 8.5 MB  | ✅ Yes | External source            | ✅ Git-LFS configured (awaiting file) |
| **mouse.mp4**   | `source/mouse.mp4`         | Source Video (MP4)     | 1.2 MB  | ❌ No  | External source            | ⚠️ Ignored                             |

**Total Size:** 11.6 MB
**Tracked:** 4 assets (9.5 MB with Git-LFS)
**Ignored:** 1 asset (1.2 MB)

## Asset Manifest

The authoritative source for asset metadata is `src/pyglet_readme/assets/manifest.yaml`, which documents:

- Asset paths and types
- Dimensions and scaling factors
- Format and sample rates
- Tracked vs. ignored status
- Description and usage

## Commit Strategy

### Tracked Assets (Committed to Repository)

These assets are small enough and essential enough to commit:

**kitten.png**

- PNG sprite (1040×1040 px, scaled to 104×104 in-game)
- **Why tracked:** Core game asset, small (\<1 MB)
- **Storage:** `src/pyglet_readme/assets/images/kitten.png`

**meow.wav**

- WAV sound effect (~0.5 seconds)
- **Why tracked:** Core game asset, small (\<1 MB), no external dependencies
- **Storage:** `src/pyglet_readme/assets/audio/sfx/meow.wav`

### Ignored Assets (Not in Repository)

These assets are excluded from version control to reduce repo size:

**mouse_sheet.png** (0.95 MB)

!!TODO: Check in to repository!!

- PNG sprite sheet (1000×1000 px, 10×10 grid)
- **Why ignored:** Generated from source video, can be recreated
- **Storage:** `src/pyglet_readme/assets/sprites/mouse_sheet.png`
- **Git Rule:** Listed in `.gitignore` line 17

**ambience.wav** (8.5 MB)

✅ **Git-LFS Configured**

- WAV background music loop (~30 seconds)
- **Why tracked with Git-LFS:** Core game asset needed for full functionality; large file requires LFS instead of direct commit
- **Storage:** `src/pyglet_readme/assets/audio/music/ambience.wav`
- **Git Rule:** Tracked via Git-LFS (`.gitattributes` line 3)
- **Status:** Awaiting source file (see Restoration section)

**mouse.mp4** (1.2 MB)

- MP4 source video for sprite generation
- **Why ignored:** Source asset, not for distribution
- **Storage:** `src/pyglet_readme/assets/source/mouse.mp4`
- **Git Rule:** Listed in `.gitignore` line 14

## Asset Generation Strategy

### mouse_sheet.png Generation

The sprite sheet is generated from the source video using FFmpeg and the `SpriteSheetGenerator` class.

**Tool:** `SpriteSheetGenerator` (`src/pyglet_readme/sprite_generator.py`)

**Requirements:**

- FFmpeg (for frame extraction)
- FFprobe (for video metadata)
- Python 3.13+

**Command:**

```bash
uv run python scripts/demo_debug_logging.py  # Or integrate into asset restoration
```

**Process:**

1. Reads video metadata from `mouse.mp4` (frame count, FPS)
2. Extracts frames to PNG images
3. Arranges into 10×10 grid (100 frames per sprite sheet)
4. Saves to `sprites/mouse_sheet.png`

**Configuration:**

```python
from pyglet_readme.sprite_generator import SpriteSheetGenerator

generator = SpriteSheetGenerator()
generator.generate(
    video_path="src/pyglet_readme/assets/source/mouse.mp4",
    output_dir="src/pyglet_readme/assets/sprites",
    grid_cols=10,
    grid_rows=10,
    frame_width=100,
    frame_height=100,
)
```

### ambience.wav Restoration

**Status:** ⚠️ Source unavailable

**Source:** Envato.com (free audio catalog - no longer available)

The background music was originally downloaded from Envato.com's free audio catalog. The catalog entry is no longer accessible, so direct re-download is not possible.

**Options for Restoration:**

1. **Use backup copy** (if stored in external cloud storage or archive)
2. **Generate alternative** (procedural audio generation or royalty-free substitutes)
3. **Point to alternatives** (Creative Commons or royalty-free music libraries):
   - Freepik.com (background music)
   - PixaBay.com (royalty-free music)
   - OpenGameArt.org (game audio)

**Current Decision:** Pending - decide whether to:
- Archive a backup copy for distribution
- Generate/source alternative background music
- Document user alternatives

### mouse.mp4 Sourcing

**Status:** ✅ Documented

**Source:** AI-generated by Google Gemini (Nano Banana Pro model)

**Generation Details:**

- **Model:** Gemini AI (Nano Banana Pro)
- **Type:** AI video generation
- **Prompt:** "Generate an image of a mouse sitting up on hind legs and looking around in studio ghibli style on white background with square aspect ratio, then generate a short loopable video of this mouse looking around."
- **Style:** Studio Ghibli anime style
- **Background:** White
- **Aspect Ratio:** Square (1:1)
- **Duration:** ~10 seconds (loopable)

**Regeneration:**

To regenerate `mouse.mp4` with the same or updated style:

1. Visit [Gemini AI](https://gemini.google.com) (or appropriate Gemini API endpoint)
2. Use the model: Nano Banana Pro (or latest available)
3. Submit the prompt (or modified version)
4. Export the generated video as MP4
5. Save to `src/pyglet_readme/assets/source/mouse.mp4`
6. Run sprite sheet generation: `SpriteSheetGenerator().generate(...)`

**Notes:**

- AI-generated assets may vary between generation runs
- Prompt can be modified for different artistic styles or animations
- No external hosting/download needed; regenerate as needed

## Asset Restoration for Fresh Clones

When cloning the repository, ignored assets must be restored to run the game with full functionality.

### Current Status

**Partially Automated:**

- ✅ `mouse_sheet.png` can be generated if `mouse.mp4` is present
- ⏳ `ambience.wav` Git-LFS configured; sourcing still pending
- ❌ `mouse.mp4` sourcing not automated

### TODO: Asset Restoration Script

Create an automated script to restore missing assets:

```bash
uv run python scripts/restore_assets.py
```

This script should:

1. **Check for ignored assets**

   ```python
   missing = check_missing_assets([
       "src/pyglet_readme/assets/sprites/mouse_sheet.png",
       "src/pyglet_readme/assets/audio/music/ambience.wav",
       "src/pyglet_readme/assets/source/mouse.mp4",
   ])
   ```

2. **For mouse_sheet.png:**

   - Check if `mouse.mp4` exists
   - If yes, run `SpriteSheetGenerator`
   - If no, prompt user to download/provide `mouse.mp4`

3. **For ambience.wav:**

   - Prompt user with sourcing options
   - Provide download link or generation instructions

4. **For mouse.mp4:**

   - Check if available locally
   - Provide download instructions from external source

5. **Report status**

   - List which assets were restored
   - List which still need manual action
   - Verify asset integrity (optional: checksum validation)

### Fallback Behavior

The game is designed to handle missing ignored assets gracefully:

- **mouse_sheet.png:** Falls back to solid-color rectangle
- **ambience.wav:** Background music simply doesn't play

See `hello_world.py` lines 69-79 and 117-124 for fallback implementations.

## Asset Directory Structure

```
src/pyglet_readme/assets/
├── images/
│   ├── .gitkeep
│   └── kitten.png          [TRACKED]
├── sprites/
│   ├── .gitkeep
│   └── mouse_sheet.png     [IGNORED - generated]
├── audio/
│   ├── sfx/
│   │   ├── .gitkeep
│   │   └── meow.wav        [TRACKED]
│   └── music/
│       ├── .gitkeep
│       └── ambience.wav    [TRACKED via Git-LFS - external]
├── source/
│   ├── .gitkeep
│   └── mouse.mp4           [IGNORED - source]
└── manifest.yaml           [TRACKED - metadata]
```

## Size Constraints

To keep repository size manageable:

**Limit for tracked assets:** < 1 MB per file, < 2 MB total for new assets

**File size threshold for ignoring:** > 1 MB (see `.gitignore`)

**Total committed size target:** < 5 MB

Current committed size: **1.0 MB** ✅

## Verification

### Verify Manifest

Check that manifest matches actual assets:

```bash
uv run pytest tests/test_asset_manifest.py -v
```

### Verify Structure

Check that directory structure matches specification:

```bash
uv run pytest tests/test_asset_structure.py -v
```

### Verify Game Startup

Verify game initializes with available assets:

```bash
uv run python tests/test_startup.py -v
```

## References

- **Manifest:** `src/pyglet_readme/assets/manifest.yaml`
- **Git Rules:** `.gitignore`
- **Generator:** `src/pyglet_readme/sprite_generator.py`
- **Tests:** `tests/test_asset_*.py`
- **Entity System:** `specs/entity_system.md`

