"""Screen system for pyglet-readme game.

Provides base screen class and screen manager for multi-screen UI architecture.
"""


class ScreenNames:
    """Constants for screen name identifiers.

    Use these instead of string literals to prevent typos causing silent bugs.
    """

    SPLASH = "splash"
    GAME_START = "game_start"
    GAME_RUNNING = "game_running"
    GAME_END = "game_end"


# Imports after ScreenNames to avoid circular imports
# ruff: noqa: E402
from .base import ScreenProtocol
from .game_end import GameEndScreen
from .game_running import GameRunningScreen
from .game_start import GameStartScreen
from .splash import SplashScreen

__all__ = [
    "ScreenNames",
    "ScreenProtocol",
    "GameEndScreen",
    "GameRunningScreen",
    "GameStartScreen",
    "SplashScreen",
]
