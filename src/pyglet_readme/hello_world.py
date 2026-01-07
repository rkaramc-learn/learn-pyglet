import logging
import math

import pyglet
from pyglet.window import key, mouse

from .assets import get_loader

logger = logging.getLogger(__name__)


def run_hello_world():

    logger.info("Starting game initialization")

    # Initialize asset loader
    loader = get_loader()
    logger.debug("Asset loader initialized")

    # Verify required assets (warn on missing, but don't fail)
    required_assets = {
        "assets/images/kitten.png": "image",
        "assets/sprites/mouse_sheet.png": "image",
        "assets/audio/sfx/meow.wav": "sound",
        "assets/audio/music/ambience.wav": "sound",
    }
    loader.verify_assets(required_assets)

    logger.info("Creating game window")
    window = pyglet.window.Window()
    logger.info(f"Window created: {window.width}x{window.height}")

    label = pyglet.text.Label(
        "Hello, world!",
        font_size=36,
        x=window.width // 2,
        y=window.height // 2,
        anchor_x="center",
        anchor_y="center",
    )

    # Kitten Setup
    logger.debug("Loading kitten sprite")
    image = loader.load_image("assets/images/kitten.png")
    image.width = image.width // 10
    image.height = image.height // 10
    image_x = window.width // 2
    image_y = window.height // 2
    logger.debug(
        f"Kitten sprite loaded: {image.width}x{image.height}, position: ({image_x}, {image_y})"
    )

    # Speed is relative to window size (e.g., cross width in 10 seconds)
    base_speed = window.width / 10.0
    mouse_speed = base_speed
    kitten_speed = base_speed / 1.5
    logger.debug(f"Movement speeds - mouse: {mouse_speed:.1f}, kitten: {kitten_speed:.1f}")

    # Health & Stamina System
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    BASE_DRAIN_RATE = 20.0  # HP per second at max proximity
    PASSIVE_STAMINA_DRAIN = 2.0  # Energy per second

    mouse_health = MAX_HEALTH
    kitten_stamina = MAX_STAMINA
    game_over = False

    # Mouse Setup - with fallback for missing sprite sheet
    logger.debug("Loading mouse sprite")
    try:
        mouse_sheet = loader.load_image("assets/sprites/mouse_sheet.png")
        mouse_grid = pyglet.image.ImageGrid(mouse_sheet, 10, 10)
        mouse_anim: pyglet.image.Animation = pyglet.image.Animation.from_image_sequence(mouse_grid, 1 / 12.0)  # type: ignore[attr-defined]
        mouse_sprite = pyglet.sprite.Sprite(mouse_anim)
        logger.info("Mouse sprite loaded from sprite sheet")
    except FileNotFoundError:
        logger.warning("mouse_sheet.png not found, using fallback sprite")
        # Create a simple colored rectangle as fallback
        fallback_image = pyglet.image.SolidColorImagePattern((0, 100, 200, 255)).create_image(50, 50)
        mouse_sprite = pyglet.sprite.Sprite(fallback_image)

    mouse_sprite.scale = 0.25
    # Start at top-left
    mouse_sprite.x = 0
    mouse_sprite.y = window.height - mouse_sprite.height

    # Calculate catch range (average of max dimensions)
    kitten_max_dim = max(image.width, image.height)
    mouse_max_dim = max(mouse_sprite.width, mouse_sprite.height)
    catch_range = (kitten_max_dim + mouse_max_dim) / 2.0

    # Manual Velocity (Press-to-move)
    mouse_vx = 0.0
    mouse_vy = 0.0

    # UI Setup (Shapes)
    bar_width = 50
    bar_height = 5
    bar_offset = 20

    mouse_bar_bg = pyglet.shapes.Rectangle(0, 0, bar_width, bar_height, color=(50, 50, 50))
    mouse_bar_fg = pyglet.shapes.Rectangle(0, 0, bar_width, bar_height, color=(0, 255, 0))
    kitten_bar_bg = pyglet.shapes.Rectangle(0, 0, bar_width, bar_height, color=(50, 50, 50))
    kitten_bar_fg = pyglet.shapes.Rectangle(0, 0, bar_width, bar_height, color=(0, 255, 0))

    # Load sound - with fallback
    logger.debug("Loading sound effects")
    try:
        meow_sound = loader.load_sound("assets/audio/sfx/meow.wav", streaming=False)
        logger.info("Sound effects loaded")
    except FileNotFoundError:
        logger.warning("meow.wav not found, sound effects disabled")
        meow_sound = None

    # Load and play background music - with fallback
    logger.debug("Loading background music")
    music_player = pyglet.media.Player()
    try:
        ambience_sound = loader.load_sound("assets/audio/music/ambience.wav")
        music_player.queue(ambience_sound)
        music_player.loop = True
        music_player.play()
        logger.info("Background music loaded and playing")
    except FileNotFoundError:
        logger.warning("ambience.wav not found, background music disabled")

    was_moving = False

    # Key handler for continuous input
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    def on_key_press(symbol: int, _modifiers: int):
        nonlocal mouse_speed, image_x, image_y, was_moving
        nonlocal mouse_vx, mouse_vy
        nonlocal mouse_health, kitten_stamina, game_over

        if symbol == key.Q:
            logger.info("Quitting game")
            window.close()
        elif symbol == key.R:
            # Reset Game State
            logger.info("Resetting game")
            mouse_speed = base_speed
            image_x = window.width // 2
            image_y = window.height // 2

            mouse_sprite.x = 0
            mouse_sprite.y = window.height - mouse_sprite.height

            # Reset Physics & Stats
            mouse_vx = 0.0
            mouse_vy = 0.0
            mouse_health = MAX_HEALTH
            kitten_stamina = MAX_STAMINA
            game_over = False
            label.text = "Hello, world!"
            was_moving = False
            logger.debug("Game state reset complete")

        if game_over:
            return

        # Manual Movement Control (Sets Velocity)
        diag_factor = 0.7071  # 1/sqrt(2) to normalize diagonal speed

        if symbol == key.UP:
            mouse_vx = 0.0
            mouse_vy = mouse_speed
        elif symbol == key.DOWN:
            mouse_vx = 0.0
            mouse_vy = -mouse_speed
        elif symbol == key.LEFT:
            mouse_vx = -mouse_speed
            mouse_vy = 0.0
        elif symbol == key.RIGHT:
            mouse_vx = mouse_speed
            mouse_vy = 0.0
        # Diagonals
        elif symbol == key.HOME:  # Up-Left
            mouse_vx = -mouse_speed * diag_factor
            mouse_vy = mouse_speed * diag_factor
        elif symbol == key.PAGEUP:  # Up-Right
            mouse_vx = mouse_speed * diag_factor
            mouse_vy = mouse_speed * diag_factor
        elif symbol == key.END:  # Down-Left
            mouse_vx = -mouse_speed * diag_factor
            mouse_vy = -mouse_speed * diag_factor
        elif symbol == key.PAGEDOWN:  # Down-Right
            mouse_vx = mouse_speed * diag_factor
            mouse_vy = -mouse_speed * diag_factor
        elif symbol == key.SPACE:  # Stop
            mouse_vx = 0.0
            mouse_vy = 0.0

    def on_mouse_press(x: int, y: int, button: int, _modifiers: int):
        nonlocal mouse_vx, mouse_vy

        if game_over:
            return

        if button == mouse.LEFT:
            # Set direction towards click
            # Target center of mouse sprite for vector calculation
            current_x = mouse_sprite.x + (mouse_sprite.width / 2)
            current_y = mouse_sprite.y + (mouse_sprite.height / 2)

            dx = float(x) - current_x
            dy = float(y) - current_y

            length = math.sqrt(dx * dx + dy * dy)

            if length > 0:
                # Normalize and apply speed
                mouse_vx = (dx / length) * mouse_speed
                mouse_vy = (dy / length) * mouse_speed
            else:
                mouse_vx = 0.0
                mouse_vy = 0.0

    window.push_handlers(on_key_press=on_key_press, on_mouse_press=on_mouse_press)

    def update(dt: float):
        nonlocal image_x, image_y, was_moving
        nonlocal mouse_health, kitten_stamina, game_over
        nonlocal mouse_vx, mouse_vy

        if game_over:
            return

        # --- Mouse Movement ---
        # Manual Velocity
        mouse_sprite.x += mouse_vx * dt
        mouse_sprite.y += mouse_vy * dt

        # Clamp mouse to window bounds
        mouse_sprite.x = max(0, min(window.width - mouse_sprite.width, mouse_sprite.x))
        mouse_sprite.y = max(0, min(window.height - mouse_sprite.height, mouse_sprite.y))

        # --- Kitten Movement (AI Only) ---
        # Kitten always chases mouse now

        # Target center of mouse sprite
        tx = mouse_sprite.x + (mouse_sprite.width / 2) - (image.width / 2)
        ty = mouse_sprite.y + (mouse_sprite.height / 2) - (image.height / 2)

        dx = tx - image_x
        dy = ty - image_y
        distance = math.sqrt(dx * dx + dy * dy)

        is_moving = False
        if distance > 2.0:  # Threshold to prevent jitter
            travel = min(distance, kitten_speed * dt)

            image_x += (dx / distance) * travel
            image_y += (dy / distance) * travel
            is_moving = True

        # Clamp kitten to window bounds
        image_x = max(0, min(window.width - image.width, image_x))
        image_y = max(0, min(window.height - image.height, image_y))

        # Check if kitten stopped moving
        if was_moving and not is_moving and meow_sound:
            _ = meow_sound.play()  # Discard return value

        was_moving = is_moving

        # --- Health & Stamina Logic ---
        # Drain/Regen if within range
        if distance < catch_range:
            proximity_factor = 1.0 - (distance / catch_range)
            proximity_factor = max(0.0, min(1.0, proximity_factor))

            transfer_amount = (BASE_DRAIN_RATE * proximity_factor) * dt

            mouse_health -= transfer_amount
            kitten_stamina += transfer_amount

        # Passive Stamina Drain
        kitten_stamina -= PASSIVE_STAMINA_DRAIN * dt

        # Clamp values
        mouse_health = max(0.0, min(MAX_HEALTH, mouse_health))
        kitten_stamina = max(0.0, min(MAX_STAMINA, kitten_stamina))

        # Win/Loss Conditions
        if mouse_health <= 0:
            game_over = True
            label.text = "Caught! (Press R to Reset)"
            mouse_vx = 0.0
            mouse_vy = 0.0
            logger.info("Game Over: Mouse caught by kitten")

        elif kitten_stamina <= 0:
            game_over = True
            label.text = "You Win!! (Press R to Reset)"
            mouse_vx = 0.0
            mouse_vy = 0.0
            logger.info("Game Over: Kitten exhausted, player wins")

        # --- UI Updates ---
        # Mouse Bar
        mouse_bar_bg.x = mouse_sprite.x + (mouse_sprite.width / 2) - (bar_width / 2)
        mouse_bar_bg.y = mouse_sprite.y + mouse_sprite.height + bar_offset
        mouse_bar_fg.x = mouse_bar_bg.x
        mouse_bar_fg.y = mouse_bar_bg.y
        mouse_bar_fg.width = bar_width * (mouse_health / MAX_HEALTH)
        mouse_bar_fg.color = (0, 255, 0) if mouse_health > 30 else (255, 0, 0)

        # Kitten Bar
        kitten_bar_bg.x = image_x + (image.width / 2) - (bar_width / 2)
        kitten_bar_bg.y = image_y + image.height + bar_offset
        kitten_bar_fg.x = kitten_bar_bg.x
        kitten_bar_fg.y = kitten_bar_bg.y
        kitten_bar_fg.width = bar_width * (kitten_stamina / MAX_STAMINA)
        kitten_bar_fg.color = (0, 255, 0) if kitten_stamina > 30 else (255, 0, 0)

    logger.info("Game initialization complete, starting game loop")
    pyglet.clock.schedule_interval(update, 1 / 60.0)  # type: ignore[attr-defined]

    @window.event  # type: ignore[attr-defined]
    def on_draw() -> None:  # type: ignore[no-untyped-def]
        window.clear()
        label.draw()
        image.blit(int(image_x), int(image_y))
        mouse_sprite.draw()

        # Draw UI
        mouse_bar_bg.draw()
        mouse_bar_fg.draw()
        kitten_bar_bg.draw()
        kitten_bar_fg.draw()

    logger.info("Starting game application")
    pyglet.app.run()
    logger.info("Game application closed")


if __name__ == "__main__":
    run_hello_world()
