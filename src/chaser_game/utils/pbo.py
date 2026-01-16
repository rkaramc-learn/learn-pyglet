"""Pixel Buffer Object (PBO) manager for asynchronous GPU readback.

This utility decouples the `glReadPixels` call from the CPU by using PBOs, allowing
the transfer to happen via DMA without stalling the CPU.
"""

import ctypes
import logging
import time
from typing import Optional

import pyglet
from pyglet.gl import (
    GL_PIXEL_PACK_BUFFER,
    GL_READ_ONLY,
    GL_RGBA,
    GL_STREAM_READ,
    GL_UNSIGNED_BYTE,
    GLsizeiptr,
    gl_info,
    glBindBuffer,
    glBufferData,
    glGenBuffers,
    glMapBuffer,
    glReadPixels,
    glUnmapBuffer,
)

logger = logging.getLogger(__name__)


class PBOManager:
    """Manages Pixel Buffer Objects for asynchronous screen capture."""

    def __init__(self, width: int, height: int, count: int = 2) -> None:
        """Initialize PBO manager.

        Args:
            width: Width of the buffer.
            height: Height of the buffer.
            count: Number of buffers to cycle (default 2 for ping-pong).
        """
        self.width = width
        self.height = height
        self.count = count
        self.buffers: list[int] = []
        self.current_index = 0
        self.row_stride = width * 4  # RGBA = 4 bytes
        self.buffer_size = self.row_stride * height
        self.last_capture_duration_us: float = 0.0
        self._pending_read_index: int = -1  # Track which PBO to read from

        self._init_buffers()

    def _init_buffers(self) -> None:
        """Initialize OpenGL buffers."""
        try:
            # Check for active context first
            if not pyglet.gl.current_context:
                logger.warning("No active GL context. PBO initialization skipped.")
                return

            # Check for PBO support via global gl_info
            if not gl_info.have_extension(
                "GL_ARB_pixel_buffer_object"
            ) and not gl_info.have_version(2, 1):
                logger.warning("PBO extension not supported. Asynchronous capture unavailable.")
                return

            ids = (ctypes.c_uint * self.count)()
            glGenBuffers(self.count, ids)
            self.buffers = list(ids)

            for buf_id in self.buffers:
                glBindBuffer(GL_PIXEL_PACK_BUFFER, buf_id)
                glBufferData(
                    GL_PIXEL_PACK_BUFFER, GLsizeiptr(self.buffer_size), None, GL_STREAM_READ
                )

            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
            logger.info(f"Initialized {self.count} PBOs (size: {self.buffer_size} bytes)")

        except Exception as e:
            logger.error(f"Failed to initialize PBOs: {e}")
            self.buffers = []

    def resize(self, width: int, height: int) -> None:
        """Resize buffers."""
        if width == self.width and height == self.height:
            return

        # Cleanup old buffers? (Pyglet/GL usually handles this on context destruction,
        # but for resize we should technically delete them. For simplicity, we just
        # re-init, leaking IDs if repeated often. In a game engine we'd glDeleteBuffers.)
        # TODO: Add explicit glDeleteBuffers if resizing happens frequently.

        self.width = width
        self.height = height
        self.row_stride = width * 4
        self.buffer_size = self.row_stride * height
        self.current_index = 0
        self._init_buffers()

    def capture(self) -> Optional[bytes]:
        """Trigger a capture and return data from the PREVIOUS capture if ready.

        DEPRECATED: Use start_capture() and end_capture() for better control.
        """
        self.start_capture()
        # This will return None on the first call, which is why we're refactoring
        return self.end_capture()

    def start_capture(self) -> None:
        """Initiate asynchronous capture of the current frame.

        This writes to the NEXT buffer in the cycle. The previously used buffer
        becomes available for reading in end_capture().
        """
        if not self.buffers:
            return

        # Remember which buffer we're about to write to (for reading next frame)
        write_index = (self.current_index + 1) % self.count
        write_pbo = self.buffers[write_index]

        start = time.perf_counter()

        # Trigger read for CURRENT frame into write_pbo
        glBindBuffer(GL_PIXEL_PACK_BUFFER, write_pbo)
        glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, 0)
        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        end = time.perf_counter()
        duration = (end - start) * 1_000_000
        logger.debug(f"PBO start_capture (glReadPixels execution): {duration:.2f} us")

        # Schedule THIS buffer for reading on the NEXT end_capture call
        self._pending_read_index = write_index
        # Advance the cycle
        self.current_index = write_index

    def end_capture(self) -> Optional[bytes]:
        """Finalize capture and retrieve data.

        Reads from the buffer that was written to in the PREVIOUS start_capture call.
        This ensures the GPU has had time to complete the DMA transfer.
        """
        if not self.buffers or self._pending_read_index < 0:
            return None

        read_pbo = self.buffers[self._pending_read_index]
        self._pending_read_index = -1  # Clear pending

        start = time.perf_counter()

        glBindBuffer(GL_PIXEL_PACK_BUFFER, read_pbo)
        ptr = glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY)

        data = None
        if ptr:
            # Copy data to python bytes
            data = ctypes.string_at(ptr, self.buffer_size)
            glUnmapBuffer(GL_PIXEL_PACK_BUFFER)

        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        end = time.perf_counter()
        self.last_capture_duration_us = (end - start) * 1_000_000

        return data
