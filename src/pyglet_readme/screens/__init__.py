"""Screen system for pyglet-readme game.

Provides base screen class and screen manager for multi-screen UI architecture.
"""

from .base import Screen
from .game_end import GameEndScreen
from .game_running import GameRunningScreen
from .game_start import GameStartScreen
from .splash import SplashScreen

__all__ = ["Screen", "GameEndScreen", "GameRunningScreen", "GameStartScreen", "SplashScreen"]
