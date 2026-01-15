"""Screen system for pyglet-readme game.

Provides base screen class and screen manager for multi-screen UI architecture.
"""

from enum import StrEnum


class ScreenName(StrEnum):
    """Enumeration for screen name identifiers.

    Provides strict type safety while remaining compatible with string-based APIs.
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
    "ScreenName",
    "ScreenProtocol",
    "GameEndScreen",
    "GameRunningScreen",
    "GameStartScreen",
    "SplashScreen",
]
