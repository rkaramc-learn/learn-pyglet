"""Pixel Buffer Object (PBO) manager for asynchronous GPU readback.

This utility decouples the `glReadPixels` call from the CPU by using PBOs, allowing
the transfer to happen via DMA without stalling the CPU.
"""

import ctypes
import logging
from typing import Optional

from pyglet.gl import (
    GL_PIXEL_PACK_BUFFER,
    GL_READ_ONLY,
    GL_RGBA,
    GL_STREAM_READ,
    GL_UNSIGNED_BYTE,
    glBindBuffer,
    glBufferData,
    glGenBuffers,
    glMapBuffer,
    glReadPixels,
    glUnmapBuffer,
)
from pyglet.gl.gl_info import GLInfo

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

        self._init_buffers()

    def _init_buffers(self) -> None:
        """Initialize OpenGL buffers."""
        try:
            # Check for PBO support
            info = GLInfo()
            if not info.have_extension("GL_ARB_pixel_buffer_object") and not info.have_version(
                2, 1
            ):
                logger.warning("PBO extension not supported. Asynchronous capture unavailable.")
                return

            ids = (ctypes.c_uint * self.count)()
            glGenBuffers(self.count, ids)
            self.buffers = list(ids)

            for buf_id in self.buffers:
                glBindBuffer(GL_PIXEL_PACK_BUFFER, buf_id)
                glBufferData(GL_PIXEL_PACK_BUFFER, self.buffer_size, None, GL_STREAM_READ)

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

        Returns:
            bytes: Raw RGBA data from a previous frame, or None if not ready.
        """
        if not self.buffers:
            return None

        # Cycle index
        next_index = (self.current_index + 1) % self.count
        next_pbo = self.buffers[next_index]
        current_pbo = self.buffers[self.current_index]

        # 1. Trigger read for CURRENT frame into next_pbo
        glBindBuffer(GL_PIXEL_PACK_BUFFER, next_pbo)
        glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, 0)

        # 2. Process PREVIOUS frame from current_pbo
        glBindBuffer(GL_PIXEL_PACK_BUFFER, current_pbo)
        ptr = glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY)

        data = None
        if ptr:
            # Copy data to python bytes
            data = ctypes.string_at(ptr, self.buffer_size)
            glUnmapBuffer(GL_PIXEL_PACK_BUFFER)

        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        # Advance index
        self.current_index = next_index

        return data
