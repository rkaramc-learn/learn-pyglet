"""Game configuration with typed constants.

All magic numbers and configuration values are centralized here as a frozen dataclass
to enable easy testing, configuration management, and entity system integration.
"""

import functools

from .colors import Color


class GameConfig:
    """Game configuration with mixed static and lazy properties.

    Uses standard attributes for simple scalars (low overhead) and
    functools.cached_property for objects or computed values (lazy loading).
    """

    # Window Configuration
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600
    TARGET_FPS: float = 60.0
    FRAME_DROP_THRESHOLD: float = 0.03  # 30ms - frame drop warning threshold

    # Sprite Configuration
    KITTEN_SCALE: float = 0.1
    MOUSE_SCALE: float = 0.25
    FALLBACK_SPRITE_SIZE: int = 50

    # Animation
    MOUSE_ANIMATION_FRAME_RATE: float = 1 / 12.0

    # Movement & Speed
    WINDOW_TRAVERSAL_TIME: float = 10.0
    KITTEN_SPEED_FACTOR: float = 1.5
    DIAGONAL_MOVEMENT_FACTOR: float = 0.7071
    MOVEMENT_DISTANCE_THRESHOLD: float = 2.0

    # Starting Positions
    MOUSE_START_X_RATIO: float = 1.0 / 3.0
    MOUSE_START_Y_RATIO: float = 0.5
    KITTEN_START_X_RATIO: float = 2.0 / 3.0
    KITTEN_START_Y_RATIO: float = 0.5

    # Health & Stamina
    MAX_HEALTH: float = 100.0
    MAX_STAMINA: float = 100.0
    BASE_DRAIN_RATE: float = 20.0
    PASSIVE_STAMINA_DRAIN: float = 2.0
    LOW_HEALTH_THRESHOLD: float = 30.0

    # UI Bar Configuration
    BAR_WIDTH: int = 50
    BAR_HEIGHT: int = 5
    BAR_OFFSET: int = 20

    # Typography
    FONT_NAME: str = "Arial"
    FONT_SIZE_HERO: int = 72
    FONT_SIZE_TITLE: int = 48
    FONT_SIZE_HEADER: int = 36
    FONT_SIZE_BODY: int = 18
    FONT_SIZE_LABEL: int = 14

    # UI Layout
    UI_PADDING: int = 20
    UI_PANEL_RADIUS: int = 10
    UI_BUTTON_HEIGHT: int = 40

    # Asset Paths
    ASSET_KITTEN_IMAGE: str = "assets/images/kitten.png"
    ASSET_MOUSE_SHEET: str = "assets/sprites/mouse_sheet.png"
    ASSET_LOGO_SVG: str = "assets/images/chaser_logo.png"
    ASSET_MEOW_SOUND: str = "assets/audio/sfx/meow.wav"
    ASSET_AMBIENCE_MUSIC: str = "assets/audio/music/ambience.wav"

    # UI Text
    TEXT_HELLO_WORLD: str = "Hello, world!"

    # Lazy Loaded Colors
    # Using cached_property ensures Color objects are created only on access

    @functools.cached_property
    def COLOR_BACKGROUND(self) -> Color:
        return Color(15, 23, 42)  # Matte Slate

    @functools.cached_property
    def COLOR_PLAYER(self) -> Color:
        return Color(255, 255, 255)  # White

    @functools.cached_property
    def COLOR_ENEMY(self) -> Color:
        return Color(231, 76, 60)  # Alizarin

    @functools.cached_property
    def COLOR_TEXT(self) -> Color:
        return Color(255, 255, 255)

    @functools.cached_property
    def COLOR_TEXT_SECONDARY(self) -> Color:
        return Color(148, 163, 184)  # Slate Grey

    @functools.cached_property
    def COLOR_ACCENT(self) -> Color:
        return Color(52, 152, 219)  # Peter River

    @functools.cached_property
    def COLOR_GREEN_ACCENT(self) -> Color:
        return Color(46, 204, 113)  # Emerald

    @functools.cached_property
    def COLOR_RED_ACCENT(self) -> Color:
        return Color(231, 76, 60)  # Alizarin

    @functools.cached_property
    def COLOR_HEALTH_GOOD(self) -> Color:
        return Color(46, 204, 113)

    @functools.cached_property
    def COLOR_HEALTH_LOW(self) -> Color:
        return Color(243, 156, 18)  # Orange

    @functools.cached_property
    def COLOR_HEALTH_CRITICAL(self) -> Color:
        return Color(231, 76, 60)

    # Deprecated / Aliases
    @functools.cached_property
    def COLOR_DARK_GRAY(self) -> Color:
        return Color(50, 50, 50)

    @functools.cached_property
    def COLOR_GREEN(self) -> Color:
        return Color(46, 204, 113)

    @functools.cached_property
    def COLOR_RED(self) -> Color:
        return Color(231, 76, 60)


# Global instance
CONFIG = GameConfig()
