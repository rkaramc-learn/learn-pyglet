"""Game configuration with typed constants.

All magic numbers and configuration values are centralized here as a frozen dataclass
to enable easy testing, configuration management, and entity system integration.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    """Immutable game configuration containing all constants."""

    # Window Configuration
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600
    TARGET_FPS: float = 60.0

    # Sprite Configuration
    KITTEN_SCALE: float = 0.1  # Scale factor for kitten sprite (original size / 10)
    MOUSE_SCALE: float = 0.25  # Scale factor for mouse sprite
    FALLBACK_SPRITE_SIZE: int = 50  # Size of fallback sprite if assets missing

    # Animation
    MOUSE_ANIMATION_FRAME_RATE: float = 1 / 12.0  # Animation frames per second

    # Movement & Speed
    WINDOW_TRAVERSAL_TIME: float = 10.0  # Seconds to traverse full window width at base speed
    KITTEN_SPEED_FACTOR: float = 1.5  # Kitten speed is 1/X of mouse speed
    DIAGONAL_MOVEMENT_FACTOR: float = 0.7071  # 1/sqrt(2) for diagonal normalization
    MOVEMENT_DISTANCE_THRESHOLD: float = 2.0  # Minimum distance to prevent jitter

    # Starting Positions (as fractions of window dimensions)
    MOUSE_START_X_RATIO: float = 1.0 / 3.0  # Mouse starts at 1/3 of window width
    MOUSE_START_Y_RATIO: float = 0.5  # Mouse starts at middle of window height
    KITTEN_START_X_RATIO: float = 2.0 / 3.0  # Kitten starts at 2/3 of window width
    KITTEN_START_Y_RATIO: float = 0.5  # Kitten starts at middle of window height

    # Health & Stamina
    MAX_HEALTH: float = 100.0
    MAX_STAMINA: float = 100.0
    BASE_DRAIN_RATE: float = 20.0  # Health points per second at max proximity
    PASSIVE_STAMINA_DRAIN: float = 2.0  # Stamina points per second
    LOW_HEALTH_THRESHOLD: float = 30.0  # Health threshold for visual warning

    # UI Bar Configuration
    BAR_WIDTH: int = 50
    BAR_HEIGHT: int = 5
    BAR_OFFSET: int = 20

    # Colors (RGB tuples)
    COLOR_DARK_GRAY: tuple[int, int, int] = (50, 50, 50)
    COLOR_GREEN: tuple[int, int, int] = (0, 255, 0)
    COLOR_RED: tuple[int, int, int] = (255, 0, 0)

    # Asset Paths
    ASSET_KITTEN_IMAGE: str = "assets/images/kitten.png"
    ASSET_MOUSE_SHEET: str = "assets/sprites/mouse_sheet.png"
    ASSET_MEOW_SOUND: str = "assets/audio/sfx/meow.wav"
    ASSET_AMBIENCE_MUSIC: str = "assets/audio/music/ambience.wav"

    # UI Text
    TEXT_HELLO_WORLD: str = "Hello, world!"


# Global instance
CONFIG = GameConfig()
