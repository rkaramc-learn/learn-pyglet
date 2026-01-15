import unittest
from unittest.mock import MagicMock, patch

from chaser_game.screen_manager import ScreenManager
from chaser_game.screens.base import ScreenProtocol


class TestScreenManagerScreenshots(unittest.TestCase):
    """Test automated screenshot functionality."""

    def setUp(self) -> None:
        self.mock_window = MagicMock()
        self.manager = ScreenManager(self.mock_window)

        # Create mock screens
        self.screen_a = MagicMock(spec=ScreenProtocol)
        self.screen_b = MagicMock(spec=ScreenProtocol)

        self.manager.register_screen("screen_a", self.screen_a)
        self.manager.register_screen("screen_b", self.screen_b)

    @patch("chaser_game.screen_manager.pyglet.image.get_buffer_manager")
    @patch("chaser_game.screen_manager.datetime")
    def test_screenshot_workflow(self, mock_datetime, mock_get_buffer_manager) -> None:
        """Test full flow of screenshots: enter A -> draw -> switch B -> draw."""
        # Setup mocks
        mock_buffer = MagicMock()
        mock_get_buffer_manager.return_value.get_color_buffer.return_value = mock_buffer
        mock_datetime.datetime.now.return_value.strftime.return_value = "TIMESTAMP"

        # 1. Enter Screen A
        self.manager.set_active_screen("screen_a")

        # Should NOT capture exit (prev was None)
        # Should queue enter
        self.assertTrue(self.manager._capture_next_frame)
        self.assertEqual(mock_buffer.save.call_count, 0)

        # 2. Draw Screen A (First Frame)
        self.manager.draw()

        # Should capture enter A
        mock_buffer.save.assert_called_with(
            f"{self.manager._screenshot_dir}\\TIMESTAMP_screen_a_enter.png"
        )
        self.assertFalse(self.manager._capture_next_frame)
        mock_buffer.save.reset_mock()

        # 3. Draw Screen A (Subsequent Frame)
        self.manager.draw()
        self.assertEqual(mock_buffer.save.call_count, 0)

        # 4. Switch to Screen B
        self.manager.set_active_screen("screen_b")

        # Should capture exit A immediately
        mock_buffer.save.assert_called_with(
            f"{self.manager._screenshot_dir}\\TIMESTAMP_screen_a_exit.png"
        )
        self.assertTrue(self.manager._capture_next_frame)
        mock_buffer.save.reset_mock()

        # 5. Draw Screen B
        self.manager.draw()

        # Should capture enter B
        mock_buffer.save.assert_called_with(
            f"{self.manager._screenshot_dir}\\TIMESTAMP_screen_b_enter.png"
        )
