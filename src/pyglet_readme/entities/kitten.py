"""Kitten entity with AI chase logic and stamina system."""

from dataclasses import dataclass

from ..config import CONFIG
from ..movement import (
    Vector2,
    apply_travel_distance,
    calculate_chase_velocity,
    clamp_to_bounds,
    distance,
    is_moving,
)
from .base import Entity, EntityState


@dataclass
class Kitten(Entity):
    """AI-controlled kitten entity with chase behavior and stamina.

    Attributes:
        stamina: Current stamina points (0-MAX_STAMINA).
        is_moving: True if kitten is currently moving (for sound effects).
    """

    stamina: float = CONFIG.MAX_STAMINA
    is_moving: bool = False

    def __post_init__(self) -> None:
        """Initialize speed based on config."""
        # Kitten is slower than mouse
        self.speed = (
            CONFIG.WINDOW_WIDTH / CONFIG.WINDOW_TRAVERSAL_TIME
        ) / CONFIG.KITTEN_SPEED_FACTOR

    def update_chase_target(self, target_x: float, target_y: float) -> None:
        """Update kitten velocity to chase a target.

        Uses frame-rate-independent movement with maximum travel per frame.

        Args:
            target_x: Target x coordinate (center of mouse).
            target_y: Target y coordinate (center of mouse).
        """
        # Use center of sprite for calculation
        current_x = self.x + self.width / 2
        current_y = self.y + self.height / 2

        # Calculate if we're moving
        self.is_moving = is_moving(
            current_x,
            current_y,
            target_x,
            target_y,
            distance_threshold=CONFIG.MOVEMENT_DISTANCE_THRESHOLD,
        )

        # Calculate velocity
        velocity = calculate_chase_velocity(
            current_x=current_x,
            current_y=current_y,
            target_x=target_x,
            target_y=target_y,
            speed=self.speed,
            distance_threshold=CONFIG.MOVEMENT_DISTANCE_THRESHOLD,
        )

        self.vx = velocity.x
        self.vy = velocity.y
        self._update_state()

    def update_position(self, dt: float) -> None:
        """Update kitten position based on velocity.

        Args:
            dt: Time elapsed in seconds.
        """
        travel_distance = min(
            distance(0, 0, self.vx, self.vy) * dt, self.speed * dt
        )

        if travel_distance > 0:
            target_x = self.x + self.vx * dt
            target_y = self.y + self.vy * dt
            new_pos = apply_travel_distance(
                self.x,
                self.y,
                target_x,
                target_y,
                travel_distance,
            )
            self.x = new_pos.x
            self.y = new_pos.y

    def apply_stamina_change(self, amount: float) -> None:
        """Apply stamina change (positive or negative).

        Args:
            amount: Stamina change amount. Positive gains, negative drains.
        """
        self.stamina = max(0.0, min(CONFIG.MAX_STAMINA, self.stamina + amount))

    def has_stamina(self) -> bool:
        """Check if kitten still has stamina.

        Returns:
            True if stamina > 0, False otherwise.
        """
        return self.stamina > 0

    def get_distance_to_target(self, target_x: float, target_y: float) -> float:
        """Calculate distance to a target (for health drain calculations).

        Args:
            target_x: Target x coordinate.
            target_y: Target y coordinate.

        Returns:
            Distance in pixels.
        """
        current_x = self.x + self.width / 2
        current_y = self.y + self.height / 2
        return distance(current_x, current_y, target_x, target_y)

    def reset(self) -> None:
        """Reset kitten to initial state.

        Resets position to origin, stops movement, and restores stamina to maximum.
        """
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.stamina = CONFIG.MAX_STAMINA
        self.is_moving = False
        self.state = EntityState.IDLE

    def _update_state(self) -> None:
        """Update entity state based on current velocity."""
        if self.vx == 0 and self.vy == 0:
            self.state = EntityState.IDLE
        elif self.is_moving:
            self.state = EntityState.CHASING
        else:
            self.state = EntityState.IDLE

    # Placeholder for sprite dimensions (will be set by game)
    width: float = 0.0
    height: float = 0.0
