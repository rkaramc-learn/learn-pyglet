"""Character entity base class and specific implementations.

Encapsulates game characters (Mouse, Kitten) with position, velocity, state,
and behavior logic following center-based coordinate positioning.
"""

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import pyglet
from pyglet import sprite

from ..config import CONFIG

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class CharacterState(Enum):
    """Character movement state."""

    IDLE = "idle"
    MOVING = "moving"
    CHASING = "chasing"


@dataclass
class CharacterData:
    """Immutable data describing a character's current state."""

    center_x: float
    center_y: float
    velocity_x: float
    velocity_y: float
    state: CharacterState
    health: float
    stamina: float


class Character:
    """Base class for game characters (Mouse, Kitten).

    Manages position (center-based), velocity, state, and provides
    update/draw/input interfaces.
    """

    def __init__(
        self,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
    ) -> None:
        """Initialize character at center position.

        Args:
            center_x: Center X coordinate.
            center_y: Center Y coordinate.
            width: Character sprite width.
            height: Character sprite height.
        """
        # Position (center-based)
        self.center_x = center_x
        self.center_y = center_y

        # Dimensions
        self.width = width
        self.height = height

        # Velocity
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # State
        self.state = CharacterState.IDLE

        # Health and stamina
        self.health = CONFIG.MAX_HEALTH
        self.stamina = CONFIG.MAX_STAMINA

        # Previous position for distance calculation
        self._prev_x = center_x
        self._prev_y = center_y

        logger.debug(
            f"{self.__class__.__name__} created at ({center_x}, {center_y}), size: {width}x{height}"
        )

    def get_data(self) -> CharacterData:
        """Get immutable snapshot of character state.

        Returns:
            CharacterData containing current state.
        """
        return CharacterData(
            center_x=self.center_x,
            center_y=self.center_y,
            velocity_x=self.velocity_x,
            velocity_y=self.velocity_y,
            state=self.state,
            health=self.health,
            stamina=self.stamina,
        )

    def clamp_to_bounds(self, window_width: float, window_height: float) -> None:
        """Clamp character position to window bounds (center-based).

        Args:
            window_width: Window width in pixels.
            window_height: Window height in pixels.
        """
        half_width = self.width / 2
        half_height = self.height / 2
        self.center_x = max(half_width, min(window_width - half_width, self.center_x))
        self.center_y = max(half_height, min(window_height - half_height, self.center_y))

    def distance_to(self, other_x: float, other_y: float) -> float:
        """Calculate distance from this character to a point.

        Args:
            other_x: Target X coordinate.
            other_y: Target Y coordinate.

        Returns:
            Distance in pixels.
        """
        dx = other_x - self.center_x
        dy = other_y - self.center_y
        return math.sqrt(dx * dx + dy * dy)

    def update(self, dt: float, window_width: float, window_height: float) -> None:
        """Update character position and state based on velocity.

        Args:
            dt: Time elapsed since last update in seconds.
            window_width: Window width for bounds checking.
            window_height: Window height for bounds checking.
        """
        # Store previous position for distance tracking
        self._prev_x = self.center_x
        self._prev_y = self.center_y

        # Update position based on velocity
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt

        # Clamp to bounds
        self.clamp_to_bounds(window_width, window_height)

        # Update state based on velocity
        if self.velocity_x == 0.0 and self.velocity_y == 0.0:
            self.state = CharacterState.IDLE
        else:
            self.state = CharacterState.MOVING

    def get_distance_traveled(self) -> float:
        """Get distance traveled since last update.

        Returns:
            Distance in pixels.
        """
        dx = self.center_x - self._prev_x
        dy = self.center_y - self._prev_y
        return math.sqrt(dx * dx + dy * dy)

    def reset_health_stamina(self) -> None:
        """Reset health and stamina to maximum values."""
        self.health = CONFIG.MAX_HEALTH
        self.stamina = CONFIG.MAX_STAMINA

    def draw(self) -> None:
        """Render character (implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement draw()")


class Mouse(Character):
    """Player-controlled mouse character.

    Responds to keyboard and mouse input, tracks distance traveled.
    """

    def __init__(
        self,
        center_x: float,
        center_y: float,
        sprite_obj: sprite.Sprite,
    ) -> None:
        """Initialize mouse character.

        Args:
            center_x: Starting center X coordinate.
            center_y: Starting center Y coordinate.
            sprite_obj: Pyglet sprite for rendering.
        """
        super().__init__(center_x, center_y, sprite_obj.width, sprite_obj.height)
        self.sprite = sprite_obj
        self.total_distance = 0.0  # Cumulative distance traveled
        logger.debug(f"Mouse created at ({center_x}, {center_y})")

    def update(self, dt: float, window_width: float, window_height: float) -> None:
        """Update mouse position and track distance traveled.

        Args:
            dt: Time elapsed since last update in seconds.
            window_width: Window width for bounds checking.
            window_height: Window height for bounds checking.
        """
        super().update(dt, window_width, window_height)
        self.total_distance += self.get_distance_traveled()

    def set_velocity_from_keyboard(self, key_state: dict[int, bool]) -> None:
        """Set velocity based on keyboard input.

        Args:
            key_state: Dictionary mapping key codes to pressed state.
        """
        # This will be called by input handler with key state
        # Subclass or caller responsibility to map keys to velocity
        pass

    def set_velocity_to_target(self, target_x: float, target_y: float) -> None:
        """Set velocity toward a target point (for mouse click movement).

        Args:
            target_x: Target X coordinate.
            target_y: Target Y coordinate.
        """
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        length = math.sqrt(dx * dx + dy * dy)

        if length > 0:
            # Normalize and apply speed
            speed = CONFIG.WINDOW_WIDTH / CONFIG.WINDOW_TRAVERSAL_TIME
            self.velocity_x = (dx / length) * speed
            self.velocity_y = (dy / length) * speed
        else:
            self.velocity_x = 0.0
            self.velocity_y = 0.0

    def draw(self) -> None:
        """Render mouse sprite centered at center position."""
        # Adjust sprite position for center-based rendering
        orig_x = self.sprite.x
        orig_y = self.sprite.y
        self.sprite.x = self.center_x - self.sprite.width / 2
        self.sprite.y = self.center_y - self.sprite.height / 2
        self.sprite.draw()
        # Restore original position
        self.sprite.x = orig_x
        self.sprite.y = orig_y

    def reset(
        self,
        center_x: float,
        center_y: float,
    ) -> None:
        """Reset mouse to starting position and state.

        Args:
            center_x: Reset center X coordinate.
            center_y: Reset center Y coordinate.
        """
        self.center_x = center_x
        self.center_y = center_y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.reset_health_stamina()
        self.total_distance = 0.0
        self.state = CharacterState.IDLE
        logger.debug(f"Mouse reset to ({center_x}, {center_y})")


class Kitten(Character):
    """AI-controlled kitten character.

    Automatically chases the mouse, with configurable speed and behavior.
    """

    def __init__(
        self,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
        image: pyglet.image.AbstractImage,
    ) -> None:
        """Initialize kitten character.

        Args:
            center_x: Starting center X coordinate.
            center_y: Starting center Y coordinate.
            width: Character sprite width.
            height: Character sprite height.
            image: Pyglet image for rendering.
        """
        super().__init__(center_x, center_y, width, height)
        self.image = image
        self.speed = CONFIG.WINDOW_WIDTH / CONFIG.WINDOW_TRAVERSAL_TIME / CONFIG.KITTEN_SPEED_FACTOR
        self.was_moving = False  # Track movement state for sound effects
        logger.debug(f"Kitten created at ({center_x}, {center_y}), speed: {self.speed:.1f}")

    def chase_target(self, target_x: float, target_y: float) -> bool:
        """Move toward target position.

        Args:
            target_x: Target X coordinate.
            target_y: Target Y coordinate.

        Returns:
            True if kitten is moving, False if at target.
        """
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        is_moving = False
        if distance > CONFIG.MOVEMENT_DISTANCE_THRESHOLD:
            travel = min(distance, self.speed * (1.0 / CONFIG.TARGET_FPS))
            self.center_x += (dx / distance) * travel
            self.center_y += (dy / distance) * travel
            is_moving = True

        # Check if kitten stopped moving
        if self.was_moving and not is_moving:
            self.state = CharacterState.IDLE
        elif is_moving:
            self.state = CharacterState.CHASING

        self.was_moving = is_moving
        return is_moving

    def draw(self) -> None:
        """Render kitten image centered at center position."""
        blit_x = int(self.center_x - self.image.width / 2)
        blit_y = int(self.center_y - self.image.height / 2)
        self.image.blit(blit_x, blit_y)

    def reset(self, center_x: float, center_y: float) -> None:
        """Reset kitten to starting position and state.

        Args:
            center_x: Reset center X coordinate.
            center_y: Reset center Y coordinate.
        """
        self.center_x = center_x
        self.center_y = center_y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.reset_health_stamina()
        self.state = CharacterState.IDLE
        self.was_moving = False
        logger.debug(f"Kitten reset to ({center_x}, {center_y})")
