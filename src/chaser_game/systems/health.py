"""Health and stamina management system."""

from ..config import CONFIG
from ..entities.kitten import Kitten
from ..entities.mouse import Mouse
from ..movement import distance


def update_health_stamina(
    mouse: Mouse,
    kitten: Kitten,
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
        mouse: Mouse entity to update.
        kitten: Kitten entity to update.
        catch_range: Maximum distance for health transfer (average of sprite dimensions).
        dt: Time elapsed in seconds.
    """
    # Calculate distance between sprites
    mouse_center_x = mouse.x + mouse.width / 2
    mouse_center_y = mouse.y + mouse.height / 2
    kitten_center_x = kitten.x + kitten.width / 2
    kitten_center_y = kitten.y + kitten.height / 2

    dist = distance(mouse_center_x, mouse_center_y, kitten_center_x, kitten_center_y)

    # Proximity-based damage: the closer, the more damage
    if dist < catch_range:
        proximity_factor = 1.0 - (dist / catch_range)
        proximity_factor = max(0.0, min(1.0, proximity_factor))

        transfer_amount = (CONFIG.BASE_DRAIN_RATE * proximity_factor) * dt

        mouse.apply_health_change(-transfer_amount)
        kitten.apply_stamina_change(transfer_amount)

    # Passive stamina drain (kitten gets tired over time)
    kitten.apply_stamina_change(-CONFIG.PASSIVE_STAMINA_DRAIN * dt)
