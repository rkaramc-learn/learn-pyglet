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
        self.manager = ScreenManager(self.mock_window, capture_screenshots=True)
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
        mock_get_buffer_manager.return_value.get_color_buffer.return_value = mock_buffer
        mock_buffer.get_image_data.return_value = mock_image_data

        mock_datetime.datetime.now.return_value.strftime.return_value = "TIMESTAMP"
        mock_datetime.datetime.now.return_value.microsecond = 456789  # Sets ms to 456

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
        mock_executor.submit.assert_called_with(
            mock_image_data.save,
            f"{self.manager._screenshot_dir}\\TIMESTAMP_456_game_start_enter.png",
        )
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
        mock_executor.submit.assert_called_with(
            mock_image_data.save,
            f"{self.manager._screenshot_dir}\\TIMESTAMP_456_game_start_exit.png",
        )
        self.assertTrue(self.manager._capture_next_frame)
        mock_executor.submit.reset_mock()

        # 5. Draw Screen B
        self.manager.draw()

        # Should capture enter B
        # Should capture enter B
        mock_executor = cast(MagicMock, self.manager.executor)
        mock_executor.submit.assert_called_with(
            mock_image_data.save,
            f"{self.manager._screenshot_dir}\\TIMESTAMP_456_game_running_enter.png",
        )

    @patch("chaser_game.screen_manager.pyglet.image.get_buffer_manager")
    @patch("chaser_game.screen_manager.datetime")
    def test_manual_screenshot_trigger(self, mock_datetime, mock_get_buffer_manager) -> None:
        """Test that INSERT key triggers manual screenshot."""
        # Setup mocks
        mock_buffer = MagicMock()
        mock_image_data = MagicMock()
        mock_get_buffer_manager.return_value.get_color_buffer.return_value = mock_buffer
        mock_buffer.get_image_data.return_value = mock_image_data

        mock_datetime.datetime.now.return_value.strftime.return_value = "TIMESTAMP"
        mock_datetime.datetime.now.return_value.microsecond = 123000

        self.manager.set_active_screen(ScreenName.GAME_START)

        # Simulate INSERT key press
        self.manager.on_key_press(pyglet.window.key.INSERT, 0)

        # Should capture with 'manual' event
        mock_executor = cast(MagicMock, self.manager.executor)
        mock_executor.submit.assert_called_with(
            mock_image_data.save,
            f"{self.manager._screenshot_dir}\\TIMESTAMP_123_game_start_manual.png",
        )
