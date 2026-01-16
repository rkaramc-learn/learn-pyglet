import unittest
from unittest.mock import MagicMock, call, patch

from chaser_game.screen_manager import ScreenManager
from chaser_game.screens import ScreenName
from chaser_game.screens.game_running import GameRunningScreen
from chaser_game.types import WindowProtocol


class TestScreenManagerHandlers(unittest.TestCase):
    """Verify ScreenManager and Screens correctly manipulate the event stack."""

    def setUp(self) -> None:
        """Set up mock window and screen manager."""
        self.mock_window = MagicMock(spec=WindowProtocol)
        self.mock_window.width = 800
        self.mock_window.height = 600

        # Mock heavy dependencies BEFORE initializing screens
        with (
            patch("chaser_game.screens.game_running.get_loader") as mock_loader,
            patch("chaser_game.screens.game_running.pyglet.sprite.Sprite") as mock_sprite,
            patch("chaser_game.screens.game_running.pyglet.image.Animation.from_image_sequence"),
            patch("chaser_game.screens.game_running.pyglet.media.Player"),
            patch("chaser_game.screens.game_running.pyglet.image.ImageGrid"),
        ):
            # Setup image mock details
            mock_loader.return_value.load_image.return_value.width = 32
            mock_loader.return_value.load_image.return_value.height = 32

            # Setup sprite mock details (needed for max() comparison in init)
            # mock_sprite is the class. return_value is the instance.
            instance = mock_sprite.return_value
            instance.width = 32
            instance.height = 32

            # Initialize manager and screens
            self.manager = ScreenManager(self.mock_window)
            self.game_running_screen = GameRunningScreen(self.mock_window)

            self.manager.register_screen(ScreenName.GAME_RUNNING, self.game_running_screen)

    def test_set_active_screen_pushes_handler(self) -> None:
        """Test that setting active screen pushes it to the window stack."""
        # Reset mock calls from init
        self.mock_window.reset_mock()

        self.manager.set_active_screen(ScreenName.GAME_RUNNING)

        # Verify screen was pushed
        self.mock_window.push_handlers.assert_any_call(self.game_running_screen)

        # Verify screen.on_enter was called, which should push Mouse
        # Mouse is pushed separately
        # Mouse object is self.game_running_screen.mouse
        self.mock_window.push_handlers.assert_any_call(self.game_running_screen.mouse)

    def test_screen_transition_pops_handlers(self) -> None:
        """Test that switching screens removes old handlers."""
        # Start at Game Running
        self.manager.set_active_screen(ScreenName.GAME_RUNNING)
        self.mock_window.reset_mock()

        # Switch to itself (re-enter) or another screen.
        # Let's mock a second screen to switch TO
        mock_screen_2 = MagicMock()
        self.manager.register_screen("splash", mock_screen_2)

        self.manager.set_active_screen("splash")

        # Verify GameRunningScreen was removed
        self.mock_window.remove_handlers.assert_any_call(self.game_running_screen)

        # Verify Mouse was removed (by GameRunningScreen.on_exit)
        self.mock_window.remove_handlers.assert_any_call(self.game_running_screen.mouse)

        # Verify new screen pushed
        self.mock_window.push_handlers.assert_any_call(mock_screen_2)

    def test_handler_order_correctness(self) -> None:
        """Verify the order of pushing (Mouse should be Top)."""
        self.mock_window.reset_mock()
        self.manager.set_active_screen(ScreenName.GAME_RUNNING)

        # Order should be:
        # 1. Screen pushed (by Manager)
        # 2. Mouse pushed (by Screen.on_enter)
        # This means Mouse is Top (last pushed)

        calls = self.mock_window.push_handlers.call_args_list
        # Filter calls related to this test
        # We expect at least these two

        # assert call(screen) comes before call(mouse)
        try:
            screen_idx = calls.index(call(self.game_running_screen))
            mouse_idx = calls.index(call(self.game_running_screen.mouse))

            self.assertLess(
                screen_idx, mouse_idx, "Screen should be pushed BEFORE Mouse so Mouse is on Top"
            )
        except ValueError:
            self.fail("Expected calls to push_handlers not found")
