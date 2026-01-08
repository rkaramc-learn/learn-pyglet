"""Entity base class with position, velocity, acceleration, and state management."""

from dataclasses import dataclass, field
from enum import Enum, auto

from ..config import CONFIG


class EntityState(Enum):
    """Enumeration of entity movement states."""

    IDLE = auto()  # Not moving
    MOVING = auto()  # Active movement (player input or AI action)
    CHASING = auto()  # AI chasing a target


@dataclass
class Entity:
    """Base class for all game entities with physics and state.

    Provides:
    - Position (x, y) and velocity (vx, vy)
    - Acceleration support for future enhancements
    - State machine for entity behavior
    - Speed configuration

    This is an immutable data class that should be updated by systems,
    not mutated directly.
    """

    # Position
    x: float = 0.0
    y: float = 0.0

    # Velocity (pixels per second)
    vx: float = 0.0
    vy: float = 0.0

    # Acceleration (for future use)
    ax: float = 0.0
    ay: float = 0.0

    # Speed magnitude (pixels per second)
    speed: float = field(default_factory=lambda: CONFIG.WINDOW_WIDTH / CONFIG.WINDOW_TRAVERSAL_TIME)

    # Current state
    state: EntityState = EntityState.IDLE

    def update(self, dt: float) -> None:
        """Update entity position based on velocity and delta time.

        Args:
            dt: Time elapsed in seconds.
        """
        self.x += self.vx * dt
        self.y += self.vy * dt

    def clamp_to_bounds(
        self,
        bounds_width: float,
        bounds_height: float,
        sprite_width: float,
        sprite_height: float,
    ) -> None:
        """Clamp entity position within window bounds.

        Args:
            bounds_width: Width of the bounding area (window width).
            bounds_height: Height of the bounding area (window height).
            sprite_width: Width of the entity sprite.
            sprite_height: Height of the entity sprite.
        """
        self.x = max(0.0, min(bounds_width - sprite_width, self.x))
        self.y = max(0.0, min(bounds_height - sprite_height, self.y))

    def set_velocity(self, vx: float, vy: float) -> None:
        """Set the entity's velocity.

        Args:
            vx: X velocity in pixels per second.
            vy: Y velocity in pixels per second.
        """
        self.vx = vx
        self.vy = vy

    def stop(self) -> None:
        """Stop the entity (set velocity to zero)."""
        self.vx = 0.0
        self.vy = 0.0
