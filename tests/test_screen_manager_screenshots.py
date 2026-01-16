import unittest
from typing import cast
from unittest.mock import MagicMock, patch

import pyglet
from chaser_game.screen_manager import ScreenManager
from chaser_game.screens import ScreenName
from chaser_game.screens.base import ScreenProtocol


class TestScreenManagerScreenshots(unittest.TestCase):
    """Test automated screenshot functionality."""

    def setUp(self) -> None:
        self.mock_window = MagicMock()
        self.mock_window.width = 800
        self.mock_window.height = 600

        # Patch PBOManager and SharedMemory initialized in __init__
        with (
            patch("chaser_game.screen_manager.PBOManager") as mock_pbo_cls,
            patch("chaser_game.screen_manager.SharedMemory") as mock_shm_cls,
        ):
            self.mock_shm = MagicMock()
            self.mock_shm.name = "test_shm"
            self.mock_shm.buf = bytearray(800 * 600 * 4)  # Real buffer for assignment
            mock_shm_cls.return_value = self.mock_shm
            self.manager = ScreenManager(self.mock_window, capture_screenshots=False)
            self.mock_pbo = mock_pbo_cls.return_value
            # Default to 0 duration for setup
            self.mock_pbo.last_capture_duration_us = 0.0
        # Mock executor to prevent actual threading during tests
        self.manager.executor = MagicMock()

        # Create mock screens
        self.screen_a = MagicMock(spec=ScreenProtocol)
        self.screen_b = MagicMock(spec=ScreenProtocol)

        # Use actual ScreenName members instead of arbitrary strings
        self.manager.register_screen(ScreenName.GAME_START, self.screen_a)
        self.manager.register_screen(ScreenName.GAME_RUNNING, self.screen_b)

    @patch("chaser_game.screen_manager.pyglet.image.get_buffer_manager")
    @patch("chaser_game.screen_manager.datetime")
    def test_screenshot_workflow(self, mock_datetime, mock_get_buffer_manager) -> None:
        """Test full flow of screenshots: enter A -> draw -> switch B -> draw."""
        # Setup mocks
        mock_buffer = MagicMock()
        mock_image_data = MagicMock()
        mock_image_data.width = 800
        # Return actual bytes for SharedMemory buffer assignment
        mock_image_data.get_data.return_value = b"\x00" * (800 * 600 * 4)
        mock_get_buffer_manager.return_value.get_color_buffer.return_value = mock_buffer
        mock_buffer.get_image_data.return_value = mock_image_data

        mock_datetime.datetime.now.return_value.strftime.return_value = "TIMESTAMP"
        mock_datetime.datetime.now.return_value.microsecond = 456789  # Sets ms to 456

        # Enable auto screenshots for this test
        self.manager.capture_screenshots = True

        # 1. Enter Screen A (GAME_START)
        self.manager.set_active_screen(ScreenName.GAME_START)

        # Should NOT capture exit (prev was None)
        # Should queue enter
        self.assertTrue(self.manager._capture_next_frame)
        mock_executor = cast(MagicMock, self.manager.executor)
        self.assertEqual(mock_executor.submit.call_count, 0)
        self.assertEqual(mock_buffer.save.call_count, 0)

        # 2. Draw Screen A (First Frame)
        self.manager.draw()

        # Should capture enter A
        # Should capture enter A
        mock_executor = cast(MagicMock, self.manager.executor)
        # New API: executor.submit(_save_screenshot, raw_data, width, height, path)
        self.assertEqual(mock_executor.submit.call_count, 1)
        args, _ = mock_executor.submit.call_args
        self.assertIn("game_start_enter.png", args[5])  # args[5] is path
        self.assertFalse(self.manager._capture_next_frame)
        mock_executor.submit.reset_mock()

        # 3. Draw Screen A (Subsequent Frame)
        self.manager.draw()
        mock_executor = cast(MagicMock, self.manager.executor)
        self.assertEqual(mock_executor.submit.call_count, 0)

        # 4. Switch to Screen B (GAME_RUNNING)
        self.manager.set_active_screen(ScreenName.GAME_RUNNING)

        # Should capture exit A immediately
        # Should capture exit A immediately
        mock_executor = cast(MagicMock, self.manager.executor)
        self.assertEqual(mock_executor.submit.call_count, 1)
        args, _ = mock_executor.submit.call_args
        self.assertIn("game_start_exit.png", args[5])  # args[5] is path
        self.assertTrue(self.manager._capture_next_frame)
        mock_executor.submit.reset_mock()

        # 5. Draw Screen B
        self.manager.draw()

        # Should capture enter B
        # Should capture enter B
        mock_executor = cast(MagicMock, self.manager.executor)
        self.assertEqual(mock_executor.submit.call_count, 1)
        args, _ = mock_executor.submit.call_args
        self.assertIn("game_running_enter.png", args[5])  # args[5] is path

    @patch("chaser_game.screen_manager.pyglet.image.get_buffer_manager")
    @patch("chaser_game.screen_manager.datetime")
    def test_manual_screenshot_trigger(self, mock_datetime, mock_get_buffer_manager) -> None:
        """Test that INSERT key triggers manual screenshot (Two-Phase)."""
        # Setup mocks
        mock_buffer = MagicMock()
        mock_image_data = MagicMock()
        mock_get_buffer_manager.return_value.get_color_buffer.return_value = mock_buffer
        mock_buffer.get_image_data.return_value = mock_image_data

        mock_datetime.datetime.now.return_value.strftime.return_value = "TIMESTAMP"
        mock_datetime.datetime.now.return_value.microsecond = 123000

        self.manager.set_active_screen(ScreenName.GAME_START)

        # Mock PBO end_capture to return data (Phase 2)
        self.mock_pbo.end_capture.return_value = b"FAKE_DATA" * (800 * 600 * 4 // 9)
        self.mock_pbo.last_capture_duration_us = 100.0

        # 1. Simulate INSERT key press (Queues pending start)
        self.manager.on_key_press(pyglet.window.key.INSERT, 0)

        # Verify nothing happened yet (deferred to draw)
        self.mock_pbo.start_capture.assert_not_called()
        self.mock_pbo.end_capture.assert_not_called()

        # 2. Simulate Frame N Draw (Triggers Phase 1: Start Capture)
        self.manager.draw()

        self.mock_pbo.start_capture.assert_called_once()
        self.mock_pbo.end_capture.assert_not_called()

        # 3. Simulate Frame N+1 Update (Triggers Phase 2: Readback)
        self.manager.update(0.16)

        self.mock_pbo.end_capture.assert_called_once()

        # Should capture with 'manual' event (using correct mock call check)
        mock_executor = cast(MagicMock, self.manager.executor)
        self.assertEqual(mock_executor.submit.call_count, 1)
        args, _ = mock_executor.submit.call_args
        self.assertIn("manual", args[5])  # args[5] is filename path

    def test_pbo_resize_handling(self) -> None:
        """Test PBO is resized when window size changes."""
        self.mock_window.width = 1024
        self.mock_window.height = 768

        self.manager.update(0.1)

        self.mock_pbo.resize.assert_called_with(1024, 768)
