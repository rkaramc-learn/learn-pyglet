"""Screen manager for handling screen transitions and lifecycle.

Manages the active screen, routes input events, and orchestrates screen updates and rendering.
"""

import concurrent.futures
import datetime
import logging
import os
import time
from multiprocessing.shared_memory import SharedMemory
from typing import Any, Optional

import pyglet
from PIL import Image

from .config import CONFIG
from .screens import ScreenName
from .screens.base import ScreenProtocol
from .types import WindowProtocol
from .utils.pbo import PBOManager

logger = logging.getLogger(__name__)


def _save_screenshot_shm(shm_name: str, size: int, width: int, height: int, path: str) -> None:
    """Save screenshot from shared memory to disk (runs in separate process).

    Args:
        shm_name: Name of the SharedMemory buffer.
        size: Size of the image data in bytes.
        width: Image width.
        height: Image height.
        path: Output file path.
    """
    try:
        # Attach to existing shared memory (created by main process)
        shm = SharedMemory(name=shm_name)
        raw_data = bytes(shm.buf[:size])
        shm.close()  # Detach from this process (main process owns it)

        # Use Pillow for encoding - it releases GIL during C operations
        img = Image.frombytes("RGBA", (width, height), raw_data)
        # Flip vertically (OpenGL origin is bottom-left)
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img.save(path, "PNG")
    except Exception as e:
        # Log error in worker process
        logger.error(f"Error saving screenshot: {e}")


class ScreenManager:
    """Manages screen transitions and lifecycle.

    Keeps track of registered screens, maintains the active screen, and handles
    routing of update/draw/input calls to the active screen.
    """

    def __init__(
        self, window: WindowProtocol, capture_screenshots: bool = False, show_fps: bool = False
    ) -> None:
        """Initialize screen manager.

        Args:
            window: The pyglet game window instance.
            capture_screenshots: Whether to capture screenshots on screen transitions.
            show_fps: Whether to show the FPS counter overlay.
        """
        self.window = window
        self.screens: dict[str, ScreenProtocol] = {}
        self.active_screen: Optional[ScreenProtocol] = None
        self.active_screen_name: Optional[str] = None
        self.capture_screenshots = capture_screenshots
        self.show_fps = show_fps

        # Screenshot state
        self._capture_next_frame: bool = False
        self._pbo_capture_pending: bool = False  # Trigger start_capture
        self._pbo_readback_pending: bool = False  # Trigger end_capture
        self._screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self._screenshot_dir, exist_ok=True)
        # Process pool for offloading screenshot encoding (avoids GIL contention)
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)

        # Shared memory buffer for zero-copy transfer to worker process
        # Size: width * height * 4 (RGBA)
        self._shm_size = window.width * window.height * 4
        self._shm: Optional[SharedMemory] = None
        self._init_shared_memory()

        # PBO Manager for manual screenshots
        self.pbo_manager = PBOManager(window.width, window.height)

        # FPS Display (optional, controlled by --show-fps)
        self.fps_display: Optional[pyglet.window.FPSDisplay] = None
        if show_fps:
            self.fps_display = pyglet.window.FPSDisplay(window=self.window)

    def _init_shared_memory(self) -> None:
        """Initialize shared memory buffer for screenshot transfer."""
        try:
            self._shm = SharedMemory(create=True, size=self._shm_size)
            logger.info(f"Created SharedMemory buffer: {self._shm.name} ({self._shm_size} bytes)")
        except Exception as e:
            logger.warning(f"Failed to create SharedMemory: {e}. Falling back to pickle.")
            self._shm = None

    def _cleanup_shared_memory(self) -> None:
        """Cleanup shared memory buffer."""
        if self._shm:
            try:
                self._shm.close()
                self._shm.unlink()
                logger.debug("SharedMemory buffer cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up SharedMemory: {e}")

    def register_screen(self, name: ScreenName, screen: ScreenProtocol) -> None:
        """Register a screen in the manager.

        Args:
            name: Unique screen identifier (e.g., "splash", "game_start", "game_running")
            screen: Screen instance to register
        """
        if name in self.screens:
            logger.warning(f"Screen '{name}' already registered, replacing")
        self.screens[name] = screen
        logger.debug(f"Registered screen: {name}")

    def _capture_screenshot(self, screen_name: str, event: str) -> None:
        """Capture and save a screenshot of the current frame.

        Args:
            screen_name: Name of the screen being captured
            event: Event name (e.g., 'enter', 'exit')
        """
        start_time = time.perf_counter()
        logger.debug(f"capture START: {screen_name}, {event}, 0")
        try:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            milliseconds = int(now.microsecond / 1000)
            filename = f"{timestamp}_{milliseconds:03d}_{screen_name}_{event}.png"
            path = os.path.join(self._screenshot_dir, filename)
            logger.debug(
                f"capture FILENAME: {screen_name}, {event}, {(time.perf_counter() - start_time) * 1_000_000:.2f}"
            )

            image_data = None
            if event == "manual":
                # Mark as pending start for end of this frame
                self._pbo_capture_pending = True
                logger.debug(f"Queued PBO start_capture for: {filename}")

                # Store filename for the readback phase
                self._pending_pbo_filename = filename
                return  # Exit, we'll finish in the next frame
            else:
                # Auto screenshots use standard readback (threaded save only)
                # Get image data on main thread (fast, GL context required)
                logger.debug(
                    f"capture EVENTCAPTUREBEGIN: {screen_name}, {event}, {((time.perf_counter() - start_time) * 1_000_000):.2f}"
                )
                image_data = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()
                logger.debug(
                    f"capture EVENTCAPTUREEND: {screen_name}, {event}, {((time.perf_counter() - start_time) * 1_000_000):.2f}"
                )

            if image_data:
                # Extract raw bytes for transfer
                raw_data = image_data.get_data("RGBA", image_data.width * 4)
                logger.debug(
                    f"capture IMAGESUBMIT: {screen_name}, {event}, {((time.perf_counter() - start_time) * 1_000_000):.2f}"
                )

                # Use shared memory if available (zero-copy), else fallback to pickle
                if self._shm:
                    # Convert to bytes for memoryview compatibility
                    raw_bytes = bytes(raw_data)
                    # Copy data to shared memory buffer
                    self._shm.buf[: len(raw_bytes)] = raw_bytes
                    self.executor.submit(
                        _save_screenshot_shm,
                        self._shm.name,
                        len(raw_data),
                        self.window.width,
                        self.window.height,
                        path,
                    )
                else:
                    # Fallback: pass raw bytes (pickle overhead)
                    self.executor.submit(
                        _save_screenshot_shm,
                        "",  # No shared memory name
                        0,
                        self.window.width,
                        self.window.height,
                        path,
                    )
        except Exception as e:
            logger.error(f"Failed to initiate screenshot capture: {e}")
        finally:
            end_time = time.perf_counter()
            duration_us = (end_time - start_time) * 1_000_000
            logger.debug(f"capture END: {screen_name}, {event}, {duration_us:.2f} us")

    def set_active_screen(self, name: ScreenName) -> None:
        """Transition to a different screen.

        Calls on_exit() on the current screen and on_enter() on the new screen.
        Also manages the window event handler stack.

        Args:
            name: Name of the screen to activate

        Raises:
            ValueError: If the screen name is not registered
        """
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' not registered")

        # Exit current screen
        if self.active_screen:
            logger.debug(f"Exiting screen: {self.active_screen_name}")
            # Capture exit screenshot of the outgoing screen
            if self.capture_screenshots and self.active_screen_name:
                self._capture_screenshot(self.active_screen_name, "exit")
            self.active_screen.on_exit()

            # Remove screen from event stack
            self.window.remove_handlers(self.active_screen)

        # Enter new screen
        self.active_screen = self.screens[name]
        self.active_screen_name = name
        logger.info(f"Transitioning to screen: {name}")
        if self.active_screen:
            # Push new screen to event stack
            # This allows it to receive inputs directly (on_key_press, etc.)
            self.window.push_handlers(self.active_screen)

            self.active_screen.on_enter()
            # Queue capture for the next frame (when it's drawn)
            if self.capture_screenshots:
                self._capture_next_frame = True

    def update(self, dt: float) -> None:
        """Update active screen.

        Args:
            dt: Time elapsed since last update in seconds
        """
        # Detect frame drops (exceeds configured threshold)
        if dt > CONFIG.FRAME_DROP_THRESHOLD:
            logger.warning(f"Frame drop detected: dt = {dt * 1000:.2f} ms")

        if self.active_screen:
            self.active_screen.update(dt)

        # Resize PBO if needed (naive check)
        # Ideally capture this via an event, but checking here covers it
        if (
            self.window.width != self.pbo_manager.width
            or self.window.height != self.pbo_manager.height
        ):
            self.pbo_manager.resize(self.window.width, self.window.height)

        # 2. Phase 2: Readback (Start of Frame N+1)
        if self._pbo_readback_pending:
            logger.debug("Executing PBO end_capture (Phase 2)")
            raw_data = self.pbo_manager.end_capture()
            self._pbo_readback_pending = False

            if raw_data and hasattr(self, "_pending_pbo_filename"):
                logger.info(
                    f"PBO capture finished. Duration: {self.pbo_manager.last_capture_duration_us:.2f} us"
                )

                path = os.path.join(self._screenshot_dir, self._pending_pbo_filename)
                logger.info("Submitting screenshot save to background process")

                # Use shared memory if available (zero-copy), else fallback
                if self._shm:
                    # Convert to bytes for memoryview compatibility
                    raw_bytes = bytes(raw_data)
                    # Copy data to shared memory buffer
                    self._shm.buf[: len(raw_bytes)] = raw_bytes
                    self.executor.submit(
                        _save_screenshot_shm,
                        self._shm.name,
                        len(raw_bytes),
                        self.window.width,
                        self.window.height,
                        path,
                    )
                else:
                    # Fallback: no shared memory (error logged at init)
                    logger.warning("SharedMemory unavailable, skipping save")

                logger.info(f"Screenshot task submitted: {self._pending_pbo_filename}")

    @property
    def last_capture_duration_us(self) -> float:
        """Get duration of last manual screenshot capture in microseconds."""
        return self.pbo_manager.last_capture_duration_us

    def on_draw(self) -> None:
        """Draw active screen.

        Called automatically by pyglet window event loop.
        """
        self.window.clear()
        if self.active_screen:
            self.active_screen.draw()

            # If queued, capture the frame we just drew
            if self._capture_next_frame and self.active_screen_name:
                self._capture_screenshot(self.active_screen_name, "enter")
                self._capture_next_frame = False

            # 1. Phase 1: Start Capture (End of Frame N)
            if self._pbo_capture_pending:
                logger.debug("Executing PBO start_capture (Phase 1)")
                self.pbo_manager.start_capture()
                self._pbo_capture_pending = False
                self._pbo_readback_pending = True

        # Draw FPS overlay (if enabled)
        if self.fps_display:
            self.fps_display.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> Any:
        """Handle global key press events.

        Args:
            symbol: Key symbol
            modifiers: Modifier keys
        """
        # Global hotkeys
        if symbol == pyglet.window.key.INSERT:
            logger.info("Manual screenshot key press detected (INSERT)")
            self._capture_screenshot(self.active_screen_name or "global", "manual")
            return pyglet.event.EVENT_HANDLED

        # We no longer strictly route to active_screen here;
        # active_screen is pushed to the stack and receives events directly.
        # However, if we want to ensure global keys are handled BEFORE the screen,
        # ScreenManager should be pushed AFTER the screen?
        # Typically ScreenManager is pushed once at startup.
        # Then Screens are pushed on top.
        # So Screens receive events FIRST.
        # If Screen consumes event (returns True), ScreenManager never sees it.
        # If Screen passes (returns None/False), ScreenManager handles it.
        # This means INSERT works globally unless a Screen consumes it. Proper behavior.

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Handle global mouse press events.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button
            modifiers: Modifier keys
        """
        # Currently no global mouse handling needed.
        # Active screen receives events directly via stack.
        pass
