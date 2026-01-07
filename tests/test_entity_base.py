"""Tests for the Entity base class."""

import unittest

from pyglet_readme.config import CONFIG
from pyglet_readme.entities.base import Entity, EntityState


class TestEntityState(unittest.TestCase):
    """Test the EntityState enum."""

    def test_entity_state_values(self) -> None:
        """Test that EntityState enum has required values."""
        self.assertEqual(EntityState.IDLE.name, "IDLE")
        self.assertEqual(EntityState.MOVING.name, "MOVING")
        self.assertEqual(EntityState.CHASING.name, "CHASING")

    def test_entity_state_uniqueness(self) -> None:
        """Test that EntityState values are unique."""
        states = [EntityState.IDLE, EntityState.MOVING, EntityState.CHASING]
        self.assertEqual(len(states), len(set(states)))


class TestEntity(unittest.TestCase):
    """Test the Entity base class."""

    def test_entity_creation_defaults(self) -> None:
        """Test creating an entity with default values."""
        entity = Entity()
        self.assertEqual(entity.x, 0.0)
        self.assertEqual(entity.y, 0.0)
        self.assertEqual(entity.vx, 0.0)
        self.assertEqual(entity.vy, 0.0)
        self.assertEqual(entity.ax, 0.0)
        self.assertEqual(entity.ay, 0.0)
        self.assertEqual(entity.state, EntityState.IDLE)

    def test_entity_creation_with_position(self) -> None:
        """Test creating an entity with custom position."""
        entity = Entity(x=100.0, y=200.0)
        self.assertEqual(entity.x, 100.0)
        self.assertEqual(entity.y, 200.0)

    def test_entity_creation_with_velocity(self) -> None:
        """Test creating an entity with custom velocity."""
        entity = Entity(vx=50.0, vy=-30.0)
        self.assertEqual(entity.vx, 50.0)
        self.assertEqual(entity.vy, -30.0)

    def test_entity_creation_with_speed(self) -> None:
        """Test creating an entity with custom speed."""
        entity = Entity(speed=150.0)
        self.assertEqual(entity.speed, 150.0)

    def test_entity_default_speed_calculation(self) -> None:
        """Test that default speed is calculated from config."""
        entity = Entity()
        expected_speed = CONFIG.WINDOW_WIDTH / CONFIG.WINDOW_TRAVERSAL_TIME
        self.assertEqual(entity.speed, expected_speed)

    def test_entity_update_position(self) -> None:
        """Test updating entity position based on velocity and time."""
        entity = Entity(x=0.0, y=0.0, vx=100.0, vy=50.0)
        entity.update(dt=1.0)
        self.assertEqual(entity.x, 100.0)
        self.assertEqual(entity.y, 50.0)

    def test_entity_update_position_with_delta_time(self) -> None:
        """Test position update with fractional delta time."""
        entity = Entity(x=0.0, y=0.0, vx=100.0, vy=50.0)
        entity.update(dt=0.5)
        self.assertEqual(entity.x, 50.0)
        self.assertEqual(entity.y, 25.0)

    def test_entity_update_position_negative_velocity(self) -> None:
        """Test position update with negative velocity."""
        entity = Entity(x=100.0, y=100.0, vx=-20.0, vy=-10.0)
        entity.update(dt=1.0)
        self.assertEqual(entity.x, 80.0)
        self.assertEqual(entity.y, 90.0)

    def test_entity_clamp_to_bounds_inside(self) -> None:
        """Test that entity inside bounds is not clamped."""
        entity = Entity(x=50.0, y=50.0)
        entity.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(entity.x, 50.0)
        self.assertEqual(entity.y, 50.0)

    def test_entity_clamp_to_bounds_left(self) -> None:
        """Test clamping entity outside left boundary."""
        entity = Entity(x=-10.0, y=50.0)
        entity.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(entity.x, 0.0)
        self.assertEqual(entity.y, 50.0)

    def test_entity_clamp_to_bounds_right(self) -> None:
        """Test clamping entity outside right boundary."""
        entity = Entity(x=800.0, y=50.0)
        entity.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        # x should be clamped to (800 - 32) = 768
        self.assertEqual(entity.x, 768.0)
        self.assertEqual(entity.y, 50.0)

    def test_entity_clamp_to_bounds_top(self) -> None:
        """Test clamping entity outside top boundary."""
        entity = Entity(x=50.0, y=-10.0)
        entity.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(entity.x, 50.0)
        self.assertEqual(entity.y, 0.0)

    def test_entity_clamp_to_bounds_bottom(self) -> None:
        """Test clamping entity outside bottom boundary."""
        entity = Entity(x=50.0, y=600.0)
        entity.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(entity.x, 50.0)
        # y should be clamped to (600 - 32) = 568
        self.assertEqual(entity.y, 568.0)

    def test_entity_clamp_to_bounds_corner(self) -> None:
        """Test clamping entity at corner."""
        entity = Entity(x=-10.0, y=-10.0)
        entity.clamp_to_bounds(
            bounds_width=800.0, bounds_height=600.0,
            sprite_width=32.0, sprite_height=32.0
        )
        self.assertEqual(entity.x, 0.0)
        self.assertEqual(entity.y, 0.0)

    def test_entity_set_velocity(self) -> None:
        """Test setting entity velocity."""
        entity = Entity()
        entity.set_velocity(vx=75.0, vy=-50.0)
        self.assertEqual(entity.vx, 75.0)
        self.assertEqual(entity.vy, -50.0)

    def test_entity_stop(self) -> None:
        """Test stopping entity (zero velocity)."""
        entity = Entity(vx=100.0, vy=50.0)
        entity.stop()
        self.assertEqual(entity.vx, 0.0)
        self.assertEqual(entity.vy, 0.0)

    def test_entity_state_assignment(self) -> None:
        """Test assigning entity state."""
        entity = Entity()
        self.assertEqual(entity.state, EntityState.IDLE)
        entity.state = EntityState.MOVING
        self.assertEqual(entity.state, EntityState.MOVING)


if __name__ == "__main__":
    unittest.main()
