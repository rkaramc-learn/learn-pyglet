"""Health and stamina management system."""

from typing import Protocol

from ..config import CONFIG
from ..movement import distance


class HealthEntity(Protocol):
    """Protocol for entities with health."""

    center_x: float
    center_y: float
    width: float
    height: float
    health: float


class StaminaEntity(Protocol):
    """Protocol for entities with stamina."""

    center_x: float
    center_y: float
    width: float
    height: float
    stamina: float


def update_health_stamina(
    mouse: HealthEntity,
    kitten: StaminaEntity,
    catch_range: float,
    dt: float,
) -> None:
    """Update mouse health and kitten stamina based on proximity and time.

    Proximity-based health drain:
    - Mouse loses health proportional to kitten proximity
    - Kitten gains stamina from dealing damage
    - Health transfer stops when distance exceeds catch range

    Stamina drain:
    - Kitten loses stamina continuously (passive drain)

    Args:
        mouse: Mouse entity with health attribute.
        kitten: Kitten entity with stamina attribute.
        catch_range: Maximum distance for health transfer.
        dt: Time elapsed in seconds.
    """
    # Calculate distance between sprite centers
    dist = distance(mouse.center_x, mouse.center_y, kitten.center_x, kitten.center_y)

    # Proximity-based damage: the closer, the more damage
    if dist < catch_range:
        proximity_factor = 1.0 - (dist / catch_range)
        proximity_factor = max(0.0, min(1.0, proximity_factor))

        transfer_amount = (CONFIG.BASE_DRAIN_RATE * proximity_factor) * dt

        mouse.health -= transfer_amount
        kitten.stamina += transfer_amount

    # Passive stamina drain (kitten gets tired over time)
    kitten.stamina -= CONFIG.PASSIVE_STAMINA_DRAIN * dt

    # Clamp values
    mouse.health = max(0.0, min(CONFIG.MAX_HEALTH, mouse.health))
    kitten.stamina = max(0.0, min(CONFIG.MAX_STAMINA, kitten.stamina))
