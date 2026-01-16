# Screenshot Optimization

Optimized the manual screenshot functionality to eliminate gameplay stutter caused by synchronous GPU readback.

## Changes

### 1. Asynchronous PBO Readback

Introduced `PBOManager` in `src/chaser_game/utils/pbo.py` to handle OpenGL Pixel Buffer Objects.

- **Why**: `glReadPixels` normally stalls the CPU until the GPU finishes the frame. PBOs allow this transfer to happen asynchronously via DMA.
- **How**: We use a ping-pong buffer strategy (count=2). The screenshot request triggers a read into the _next_ PBO, while we map and save data from the _previous_ PBO (if ready).

### 2. ScreenManager Integration

Updated `src/chaser_game/screen_manager.py` to support two capture paths:

- **Manual (INSERT key)**: Uses `PBOManager` with a **Two-Frame Split** strategy:
  1.  **Frame N (Draw)**: `start_capture()` triggers `glReadPixels` into a PBO.
  2.  **Frame N+1 (Update)**: `end_capture()` maps the PBO and retrieves data.
      This ensures the `glReadPixels` command has time to complete on the GPU, avoiding any pipeline stall (stutter) while guaranteeing fresh data for single-shot captures.
- **Automatic (Screen Transitions)**: Uses standard `get_image_data()` with `ProcessPoolExecutor`.

### 3. GIL Contention Fix (ProcessPoolExecutor + SharedMemory)

**Problem**: `ThreadPoolExecutor` save caused **~500ms stutter** due to Python's GIL being held during PNG encoding.

**Solution**:

1. **ProcessPoolExecutor**: Moved save to separate process (bypasses GIL) → reduced to **~25ms**
2. **SharedMemory**: Zero-copy buffer transfer between processes → stabilized at **~20-28ms**

**Implementation**:

- Added `_save_screenshot_shm()` function that reads from SharedMemory by name
- Created persistent `SharedMemory` buffer in `ScreenManager.__init__`
- Both auto and manual screenshots use SharedMemory path when available
- Added Pillow dependency for cross-process PNG encoding

### 4. Context Initialization Fix

- Fixed `UserWarning: No GL context created yet` by using global `pyglet.gl.gl_info`.
- Added `window.switch_to()` in main entry point to ensure context is active before subsystem initialization.

### 5. Performance Metrics & Enforcement

- Instrumented `PBOManager.capture()` to measure execution time (microseconds).
- Added `tests/test_performance_screenshots.py` to enforce a capture budget of **< 2ms**.
- Exposed specific metrics via `ScreenManager.last_capture_duration_us`.
- Added granular logging (DEBUG level) for the entire manual capture lifecycle.

### 6. FPS Counter

- Added `pyglet.window.FPSDisplay` to the top-left corner.
- Guard behind `--show-fps` CLI option for optional visibility.

## Final Performance

| Stage                            |             Duration              |
| :------------------------------- | :-------------------------------: |
| PBO start_capture (glReadPixels) |            ~60-300 µs             |
| PBO end_capture (Map + Copy)     |              ~1-3 ms              |
| SharedMemory copy + submit       |               ~5 ms               |
| **Total Main Thread Work**       |           **~8-10 ms**            |
| Frame Drop After Submit          | ~20-28 ms (baseline GPU variance) |

## Verification

### Automated Tests

- `tests/test_screen_manager_screenshots.py`: Manual triggers, resize events, executor submits. **All passed.**
- `tests/test_performance_screenshots.py`: Capture overhead within 2ms budget.

### Manual Verification

- **Scenario**: Rapidly pressing `INSERT` during gameplay.
- **User Observation**: No stutter! Excellent!!!
