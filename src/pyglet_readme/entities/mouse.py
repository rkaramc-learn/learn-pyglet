"""Mouse entity with player input handling and health system."""

from dataclasses import dataclass

from ..config import CONFIG
from ..movement import (
    Vector2,
    calculate_click_velocity,
    calculate_keyboard_velocity,
    clamp_to_bounds,
    update_position,
)
from .base import Entity, EntityState


@dataclass
class Mouse(Entity):
    """Player-controlled mouse entity with health system.

    Attributes:
        health: Current health points (0-MAX_HEALTH).
    """

    health: float = CONFIG.MAX_HEALTH

    def update_from_keyboard(
        self,
        up: bool,
        down: bool,
        left: bool,
        right: bool,
    ) -> None:
        """Update mouse velocity from keyboard input.

        Args:
            up: True if up key is pressed.
            down: True if down key is pressed.
            left: True if left key is pressed.
            right: True if right key is pressed.
        """
        velocity = calculate_keyboard_velocity(
            up=up,
            down=down,
            left=left,
            right=right,
            speed=self.speed,
            diagonal_factor=CONFIG.DIAGONAL_MOVEMENT_FACTOR,
        )
        self.vx = velocity.x
        self.vy = velocity.y
        self._update_state()

    def update_from_click(self, target_x: float, target_y: float) -> None:
        """Update mouse velocity toward a clicked location.

        Args:
            target_x: X coordinate of click.
            target_y: Y coordinate of click.
        """
        # Use center of sprite for calculation
        current_x = self.x + self.width / 2
        current_y = self.y + self.height / 2

        velocity = calculate_click_velocity(
            current_x=current_x,
            current_y=current_y,
            target_x=target_x,
            target_y=target_y,
            speed=self.speed,
        )
        self.vx = velocity.x
        self.vy = velocity.y
        self._update_state()

    def update_position(self, dt: float) -> None:
        """Update mouse position based on velocity.

        Args:
            dt: Time elapsed in seconds.
        """
        new_pos = update_position(self.x, self.y, self.vx, self.vy, dt)
        self.x = new_pos.x
        self.y = new_pos.y

    def apply_health_change(self, amount: float) -> None:
        """Apply health change (positive or negative).

        Args:
            amount: Health change amount. Positive heals, negative damages.
        """
        self.health = max(0.0, min(CONFIG.MAX_HEALTH, self.health + amount))

    def is_alive(self) -> bool:
        """Check if mouse is still alive.

        Returns:
            True if health > 0, False otherwise.
        """
        return self.health > 0

    def reset(self) -> None:
        """Reset mouse to initial state.

        Resets position to origin, stops movement, and restores health to maximum.
        """
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.health = CONFIG.MAX_HEALTH
        self.state = EntityState.IDLE

    def _update_state(self) -> None:
        """Update entity state based on current velocity."""
        if self.vx == 0 and self.vy == 0:
            self.state = EntityState.IDLE
        else:
            self.state = EntityState.MOVING

    # Placeholder for sprite dimensions (will be set by game)
    width: float = 0.0
    height: float = 0.0
