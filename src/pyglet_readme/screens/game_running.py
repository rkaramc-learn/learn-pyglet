"""Game running screen for main gameplay.

Handles sprite rendering, input, movement, health/stamina mechanics, and win/loss conditions.
"""

import logging
import math
from typing import TYPE_CHECKING

import pyglet
from pyglet.window import key, mouse

from ..assets import get_loader
from .base import Screen

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Game Configuration
KITTEN_SCALE = 0.1  # Scale factor for kitten sprite (original size / 10)
MOUSE_SCALE = 0.25  # Scale factor for mouse sprite
MOUSE_ANIMATION_FRAME_RATE = 1 / 12.0  # Animation frames per second
FALLBACK_SPRITE_SIZE = 50  # Size of fallback sprite if assets missing
WINDOW_TRAVERSAL_TIME = 10.0  # Seconds to traverse full window width at base speed
KITTEN_SPEED_FACTOR = 1.5  # Kitten speed is 1/X of mouse speed

# Health & Stamina
MAX_HEALTH = 100.0
MAX_STAMINA = 100.0
BASE_DRAIN_RATE = 20.0  # Health points per second at max proximity
PASSIVE_STAMINA_DRAIN = 2.0  # Stamina points per second

# Movement
DIAGONAL_MOVEMENT_FACTOR = 0.7071  # 1/sqrt(2) for diagonal normalization
MOVEMENT_DISTANCE_THRESHOLD = 2.0  # Minimum distance to prevent jitter

# UI Bar Configuration
BAR_WIDTH = 50
BAR_HEIGHT = 5
BAR_OFFSET = 20

# Colors (RGB tuples)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)


class GameRunningScreen(Screen):
    """Main gameplay screen.

    Manages sprite rendering, input handling, game state (health/stamina),
    movement logic, and win/loss conditions.
    """

    def __init__(self, window: "pyglet.window.Window") -> None:  # type: ignore[name-defined]
        """Initialize game running screen.

        Args:
            window: The pyglet game window instance.
        """
        super().__init__(window)

        # Asset loader
        self.loader = get_loader()

        # Initialize sprite and UI elements
        self.label = pyglet.text.Label(
            "Hello, world!",
            font_size=36,
            x=window.width // 2,
            y=window.height // 2,
            anchor_x="center",
            anchor_y="center",
        )

        # Kitten Setup
        logger.debug("Loading kitten sprite")
        kitten_image = self.loader.load_image("assets/images/kitten.png")
        kitten_image.width = int(kitten_image.width * KITTEN_SCALE)
        kitten_image.height = int(kitten_image.height * KITTEN_SCALE)
        self.kitten_image = kitten_image
        self.image_x = window.width // 2
        self.image_y = window.height // 2
        logger.debug(
            f"Kitten sprite loaded: {kitten_image.width}x{kitten_image.height}, "
            f"position: ({self.image_x}, {self.image_y})"
        )

        # Speed is relative to window size (cross window width in WINDOW_TRAVERSAL_TIME)
        self.base_speed = window.width / WINDOW_TRAVERSAL_TIME
        self.mouse_speed = self.base_speed
        self.kitten_speed = self.base_speed / KITTEN_SPEED_FACTOR
        logger.debug(
            f"Movement speeds - mouse: {self.mouse_speed:.1f}, kitten: {self.kitten_speed:.1f}"
        )

        # Game State
        self.mouse_health = MAX_HEALTH
        self.kitten_stamina = MAX_STAMINA
        self.game_over = False

        # Mouse Setup - with fallback for missing sprite sheet
        logger.debug("Loading mouse sprite")
        try:
            mouse_sheet = self.loader.load_image("assets/sprites/mouse_sheet.png")
            mouse_grid = pyglet.image.ImageGrid(mouse_sheet, 10, 10)
            mouse_anim = pyglet.image.Animation.from_image_sequence(  # type: ignore[attr-defined]
                mouse_grid, MOUSE_ANIMATION_FRAME_RATE
            )
            self.mouse_sprite = pyglet.sprite.Sprite(mouse_anim)
            logger.info("Mouse sprite loaded from sprite sheet")
        except FileNotFoundError:
            logger.warning("mouse_sheet.png not found, using fallback sprite")
            # Create a simple colored rectangle as fallback
            fallback_image = pyglet.image.SolidColorImagePattern(
                (0, 100, 200, 255)
            ).create_image(FALLBACK_SPRITE_SIZE, FALLBACK_SPRITE_SIZE)
            self.mouse_sprite = pyglet.sprite.Sprite(fallback_image)

        self.mouse_sprite.scale = MOUSE_SCALE
        # Start at top-left
        self.mouse_sprite.x = 0
        self.mouse_sprite.y = window.height - self.mouse_sprite.height

        # Calculate catch range (average of max dimensions)
        kitten_max_dim = max(kitten_image.width, kitten_image.height)
        mouse_max_dim = max(self.mouse_sprite.width, self.mouse_sprite.height)
        self.catch_range = (kitten_max_dim + mouse_max_dim) / 2.0

        # Manual Velocity (Press-to-move)
        self.mouse_vx = 0.0
        self.mouse_vy = 0.0

        # UI Setup (Shapes)
        self.mouse_bar_bg = pyglet.shapes.Rectangle(
            0, 0, BAR_WIDTH, BAR_HEIGHT, color=COLOR_DARK_GRAY
        )
        self.mouse_bar_fg = pyglet.shapes.Rectangle(
            0, 0, BAR_WIDTH, BAR_HEIGHT, color=COLOR_GREEN
        )
        self.kitten_bar_bg = pyglet.shapes.Rectangle(
            0, 0, BAR_WIDTH, BAR_HEIGHT, color=COLOR_DARK_GRAY
        )
        self.kitten_bar_fg = pyglet.shapes.Rectangle(
            0, 0, BAR_WIDTH, BAR_HEIGHT, color=COLOR_GREEN
        )

        # Load sound - with fallback
        logger.debug("Loading sound effects")
        try:
            self.meow_sound = self.loader.load_sound(
                "assets/audio/sfx/meow.wav", streaming=False
            )
            logger.info("Sound effects loaded")
        except FileNotFoundError:
            logger.warning("meow.wav not found, sound effects disabled")
            self.meow_sound = None

        # Load and play background music - with fallback
        logger.debug("Loading background music")
        self.music_player = pyglet.media.Player()
        try:
            ambience_sound = self.loader.load_sound("assets/audio/music/ambience.wav")
            self.music_player.queue(ambience_sound)
            self.music_player.loop = True
            logger.info("Background music loaded (will play on screen enter)")
        except FileNotFoundError:
            logger.warning("ambience.wav not found, background music disabled")

        self.was_moving = False

        # Key handler for continuous input
        self.keys = key.KeyStateHandler()

    def on_enter(self) -> None:
        """Called when game running screen becomes active."""
        logger.info("Game running screen started")
        self.window.push_handlers(self.keys)
        self.window.push_handlers(on_key_press=self._on_key_press, on_mouse_press=self._on_mouse_press)
        self.music_player.play()
        # Schedule update
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)  # type: ignore[attr-defined]

    def on_exit(self) -> None:
        """Called when game running screen is left."""
        logger.debug("Game running screen exited")
        self.music_player.pause()
        pyglet.clock.unschedule(self.update)  # type: ignore[attr-defined]

    def _on_key_press(self, symbol: int, _modifiers: int) -> None:
        """Handle key press events.

        Args:
            symbol: Key symbol from pyglet.window.key
            _modifiers: Modifier keys (unused)
        """
        if symbol == key.Q:
            logger.info("Quitting game")
            self.window.close()
        elif symbol == key.R:
            # Reset Game State
            logger.info("Resetting game")
            self.mouse_speed = self.base_speed
            self.image_x = self.window.width // 2
            self.image_y = self.window.height // 2

            self.mouse_sprite.x = 0
            self.mouse_sprite.y = self.window.height - self.mouse_sprite.height

            # Reset Physics & Stats
            self.mouse_vx = 0.0
            self.mouse_vy = 0.0
            self.mouse_health = MAX_HEALTH
            self.kitten_stamina = MAX_STAMINA
            self.game_over = False
            self.label.text = "Hello, world!"
            self.was_moving = False
            logger.debug("Game state reset complete")

        if self.game_over:
            return

        # Manual Movement Control (Sets Velocity)
        if symbol == key.UP:
            self.mouse_vx = 0.0
            self.mouse_vy = self.mouse_speed
        elif symbol == key.DOWN:
            self.mouse_vx = 0.0
            self.mouse_vy = -self.mouse_speed
        elif symbol == key.LEFT:
            self.mouse_vx = -self.mouse_speed
            self.mouse_vy = 0.0
        elif symbol == key.RIGHT:
            self.mouse_vx = self.mouse_speed
            self.mouse_vy = 0.0
        # Diagonals
        elif symbol == key.HOME:  # Up-Left
            self.mouse_vx = -self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
            self.mouse_vy = self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.PAGEUP:  # Up-Right
            self.mouse_vx = self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
            self.mouse_vy = self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.END:  # Down-Left
            self.mouse_vx = -self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
            self.mouse_vy = -self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.PAGEDOWN:  # Down-Right
            self.mouse_vx = self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
            self.mouse_vy = -self.mouse_speed * DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.SPACE:  # Stop
            self.mouse_vx = 0.0
            self.mouse_vy = 0.0

    def _on_mouse_press(self, x: int, y: int, button: int, _modifiers: int) -> None:
        """Handle mouse press events.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button from pyglet.window.mouse
            _modifiers: Modifier keys (unused)
        """
        if self.game_over:
            return

        if button == mouse.LEFT:
            # Set direction towards click
            # Target center of mouse sprite for vector calculation
            current_x = self.mouse_sprite.x + (self.mouse_sprite.width / 2)
            current_y = self.mouse_sprite.y + (self.mouse_sprite.height / 2)

            dx = float(x) - current_x
            dy = float(y) - current_y

            length = math.sqrt(dx * dx + dy * dy)

            if length > 0:
                # Normalize and apply speed
                self.mouse_vx = (dx / length) * self.mouse_speed
                self.mouse_vy = (dy / length) * self.mouse_speed
            else:
                self.mouse_vx = 0.0
                self.mouse_vy = 0.0

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle key press events (Screen base class interface).

        Args:
            symbol: Key symbol
            modifiers: Modifier keys
        """
        self._on_key_press(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Handle mouse press events (Screen base class interface).

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button
            modifiers: Modifier keys
        """
        self._on_mouse_press(x, y, button, modifiers)

    def _update_mouse_position(self, dt: float) -> None:
        """Update mouse sprite position based on velocity.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        self.mouse_sprite.x += self.mouse_vx * dt
        self.mouse_sprite.y += self.mouse_vy * dt

        # Clamp mouse to window bounds
        self.mouse_sprite.x = max(
            0, min(self.window.width - self.mouse_sprite.width, self.mouse_sprite.x)
        )
        self.mouse_sprite.y = max(
            0, min(self.window.height - self.mouse_sprite.height, self.mouse_sprite.y)
        )

    def _update_kitten_position(self, dt: float) -> float:
        """Update kitten position chasing the mouse.

        Args:
            dt: Time elapsed since last update in seconds.

        Returns:
            Distance to mouse sprite for use in health calculations.
        """
        # Target center of mouse sprite
        tx = (
            self.mouse_sprite.x
            + (self.mouse_sprite.width / 2)
            - (self.kitten_image.width / 2)
        )
        ty = (
            self.mouse_sprite.y
            + (self.mouse_sprite.height / 2)
            - (self.kitten_image.height / 2)
        )

        dx = tx - self.image_x
        dy = ty - self.image_y
        distance = math.sqrt(dx * dx + dy * dy)

        is_moving = False
        if distance > MOVEMENT_DISTANCE_THRESHOLD:
            travel = min(distance, self.kitten_speed * dt)

            self.image_x += (dx / distance) * travel
            self.image_y += (dy / distance) * travel
            is_moving = True

        # Clamp kitten to window bounds
        self.image_x = max(
            0, min(self.window.width - self.kitten_image.width, self.image_x)
        )
        self.image_y = max(
            0, min(self.window.height - self.kitten_image.height, self.image_y)
        )

        # Check if kitten stopped moving
        if self.was_moving and not is_moving and self.meow_sound:
            _ = self.meow_sound.play()  # Discard return value

        self.was_moving = is_moving
        return distance

    def _update_health_stamina(self, distance: float, dt: float) -> None:
        """Update health and stamina based on proximity and time.

        Args:
            distance: Current distance between kitten and mouse sprites.
            dt: Time elapsed since last update in seconds.
        """
        # Drain/Regen if within range
        if distance < self.catch_range:
            proximity_factor = 1.0 - (distance / self.catch_range)
            proximity_factor = max(0.0, min(1.0, proximity_factor))

            transfer_amount = (BASE_DRAIN_RATE * proximity_factor) * dt

            self.mouse_health -= transfer_amount
            self.kitten_stamina += transfer_amount

        # Passive Stamina Drain
        self.kitten_stamina -= PASSIVE_STAMINA_DRAIN * dt

        # Clamp values
        self.mouse_health = max(0.0, min(MAX_HEALTH, self.mouse_health))
        self.kitten_stamina = max(0.0, min(MAX_STAMINA, self.kitten_stamina))

    def _check_win_loss_conditions(self) -> None:
        """Check and handle win/loss game conditions."""
        if self.mouse_health <= 0:
            self.game_over = True
            self.mouse_vx = 0.0
            self.mouse_vy = 0.0
            logger.info("Game Over: Mouse caught by kitten")
            self._transition_to_game_end(is_win=False)

        elif self.kitten_stamina <= 0:
            self.game_over = True
            self.mouse_vx = 0.0
            self.mouse_vy = 0.0
            logger.info("Game Over: Kitten exhausted, player wins")
            self._transition_to_game_end(is_win=True)

    def _transition_to_game_end(self, is_win: bool) -> None:
        """Transition to the game end screen.

        Args:
            is_win: True if player won, False if player lost.
        """
        from ..screen_manager import ScreenManager

        manager = getattr(self.window, "_screen_manager", None)
        if isinstance(manager, ScreenManager):
            game_end_screen = manager.screens.get("game_end")
            if game_end_screen:
                game_end_screen.set_outcome(is_win)  # type: ignore[attr-defined]
            manager.set_active_screen("game_end")

    def _update_ui_bars(self) -> None:
        """Update health and stamina bar positions and values."""
        # Mouse Bar
        self.mouse_bar_bg.x = (
            self.mouse_sprite.x + (self.mouse_sprite.width / 2) - (BAR_WIDTH / 2)
        )
        self.mouse_bar_bg.y = self.mouse_sprite.y + self.mouse_sprite.height + BAR_OFFSET
        self.mouse_bar_fg.x = self.mouse_bar_bg.x
        self.mouse_bar_fg.y = self.mouse_bar_bg.y
        self.mouse_bar_fg.width = BAR_WIDTH * (self.mouse_health / MAX_HEALTH)
        self.mouse_bar_fg.color = COLOR_GREEN if self.mouse_health > 30 else COLOR_RED

        # Kitten Bar
        self.kitten_bar_bg.x = (
            self.image_x + (self.kitten_image.width / 2) - (BAR_WIDTH / 2)
        )
        self.kitten_bar_bg.y = self.image_y + self.kitten_image.height + BAR_OFFSET
        self.kitten_bar_fg.x = self.kitten_bar_bg.x
        self.kitten_bar_fg.y = self.kitten_bar_bg.y
        self.kitten_bar_fg.width = BAR_WIDTH * (self.kitten_stamina / MAX_STAMINA)
        self.kitten_bar_fg.color = COLOR_GREEN if self.kitten_stamina > 30 else COLOR_RED

    def update(self, dt: float) -> None:
        """Update game running screen state.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        if self.game_over:
            return

        self._update_mouse_position(dt)
        distance = self._update_kitten_position(dt)
        self._update_health_stamina(distance, dt)
        self._check_win_loss_conditions()
        self._update_ui_bars()

    def draw(self) -> None:
        """Render game running screen content."""
        self.label.draw()
        self.kitten_image.blit(int(self.image_x), int(self.image_y))
        self.mouse_sprite.draw()

        # Draw UI
        self.mouse_bar_bg.draw()
        self.mouse_bar_fg.draw()
        self.kitten_bar_bg.draw()
        self.kitten_bar_fg.draw()
