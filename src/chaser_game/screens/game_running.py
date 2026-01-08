"""Game running screen for main gameplay.

Handles sprite rendering, input, movement, health/stamina mechanics, and win/loss conditions.
"""

import logging
from typing import Any

import pyglet
from pyglet.window import key, mouse

from ..assets import get_loader
from ..config import CONFIG
from ..entities import Kitten, Mouse
from ..types import AudioProtocol, WindowProtocol
from .base import ScreenProtocol

logger = logging.getLogger(__name__)


class GameRunningScreen(ScreenProtocol):
    """Main gameplay screen.

    Manages sprite rendering, input handling, game state (health/stamina),
    movement logic, and win/loss conditions.
    """

    music_player: AudioProtocol

    def __init__(self, window: WindowProtocol) -> None:
        """Initialize game running screen.

        Args:
            window: The pyglet game window instance.
        """
        super().__init__(window)

        # Asset loader
        self.loader = get_loader()

        # Kitten Setup
        logger.debug("Loading kitten sprite")
        kitten_image = self.loader.load_image(CONFIG.ASSET_KITTEN_IMAGE)
        kitten_image.width = int(kitten_image.width * CONFIG.KITTEN_SCALE)
        kitten_image.height = int(kitten_image.height * CONFIG.KITTEN_SCALE)
        self.kitten_image = kitten_image
        logger.debug(f"Kitten sprite loaded: {kitten_image.width}x{kitten_image.height}")

        # Create kitten entity
        kitten_start_x = window.width * CONFIG.KITTEN_START_X_RATIO
        kitten_start_y = window.height * CONFIG.KITTEN_START_Y_RATIO
        self.kitten = Kitten(
            kitten_start_x,
            kitten_start_y,
            kitten_image.width,
            kitten_image.height,
            kitten_image,
        )

        # Mouse Setup - with fallback for missing sprite sheet
        logger.debug("Loading mouse sprite")
        try:
            mouse_sheet = self.loader.load_image(CONFIG.ASSET_MOUSE_SHEET)
            mouse_grid = pyglet.image.ImageGrid(mouse_sheet, 10, 10)
            # Create animation from image grid using the internal Animation API
            # Animation.from_image_sequence creates an animation from grid images
            mouse_anim: Any = pyglet.image.Animation.from_image_sequence(  # type: ignore[attr-defined]
                mouse_grid, CONFIG.MOUSE_ANIMATION_FRAME_RATE
            )
            mouse_sprite = pyglet.sprite.Sprite(mouse_anim)
            logger.info("Mouse sprite loaded from sprite sheet")
        except FileNotFoundError:
            logger.warning("mouse_sheet.png not found, using fallback sprite")
            # Create a simple colored rectangle as fallback
            fallback_image = pyglet.image.SolidColorImagePattern((0, 100, 200, 255)).create_image(
                CONFIG.FALLBACK_SPRITE_SIZE, CONFIG.FALLBACK_SPRITE_SIZE
            )
            mouse_sprite = pyglet.sprite.Sprite(fallback_image)

        mouse_sprite.scale = CONFIG.MOUSE_SCALE
        logger.debug(f"Mouse sprite loaded and scaled: {mouse_sprite.width}x{mouse_sprite.height}")

        # Create mouse entity
        mouse_start_x = window.width * CONFIG.MOUSE_START_X_RATIO
        mouse_start_y = window.height * CONFIG.MOUSE_START_Y_RATIO
        self.mouse = Mouse(mouse_start_x, mouse_start_y, mouse_sprite)

        # Calculate catch range (average of max dimensions)
        kitten_max_dim = max(kitten_image.width, kitten_image.height)
        mouse_max_dim = max(mouse_sprite.width, mouse_sprite.height)
        self.catch_range = (kitten_max_dim + mouse_max_dim) / 2.0

        # UI Setup (Shapes)
        self.mouse_bar_bg = pyglet.shapes.Rectangle(
            0, 0, CONFIG.BAR_WIDTH, CONFIG.BAR_HEIGHT, color=CONFIG.COLOR_DARK_GRAY
        )
        self.mouse_bar_fg = pyglet.shapes.Rectangle(
            0, 0, CONFIG.BAR_WIDTH, CONFIG.BAR_HEIGHT, color=CONFIG.COLOR_GREEN
        )
        self.kitten_bar_bg = pyglet.shapes.Rectangle(
            0, 0, CONFIG.BAR_WIDTH, CONFIG.BAR_HEIGHT, color=CONFIG.COLOR_DARK_GRAY
        )
        self.kitten_bar_fg = pyglet.shapes.Rectangle(
            0, 0, CONFIG.BAR_WIDTH, CONFIG.BAR_HEIGHT, color=CONFIG.COLOR_GREEN
        )

        # Load sound - with fallback
        logger.debug("Loading sound effects")
        try:
            self.meow_sound = self.loader.load_sound(CONFIG.ASSET_MEOW_SOUND, streaming=False)
            logger.info("Sound effects loaded")
        except FileNotFoundError:
            logger.warning("meow.wav not found, sound effects disabled")
            self.meow_sound = None

        # Load and play background music - with fallback
        logger.debug("Loading background music")
        self.music_player = pyglet.media.Player()
        try:
            ambience_sound = self.loader.load_sound(CONFIG.ASSET_AMBIENCE_MUSIC)
            self.music_player.queue(ambience_sound)
            self.music_player.loop = True
            logger.info("Background music loaded (will play on screen enter)")
        except FileNotFoundError:
            logger.warning("ambience.wav not found, background music disabled")

        # Key handler for continuous input
        self.keys = key.KeyStateHandler()

        # Game statistics
        self.elapsed_time = 0.0  # Time survived in seconds

        # Game state
        self.game_over = False

    def on_enter(self) -> None:
        """Called when game running screen becomes active."""
        logger.info("Game running screen started")
        self.window.push_handlers(self.keys)
        self.window.push_handlers(
            on_key_press=self._on_key_press, on_mouse_press=self._on_mouse_press
        )
        self.music_player.play()

        # Reset entities
        self.mouse.reset(
            self.window.width * CONFIG.MOUSE_START_X_RATIO,
            self.window.height * CONFIG.MOUSE_START_Y_RATIO,
        )
        self.kitten.reset(
            self.window.width * CONFIG.KITTEN_START_X_RATIO,
            self.window.height * CONFIG.KITTEN_START_Y_RATIO,
        )

        # Reset game statistics
        self.elapsed_time = 0.0
        self.game_over = False

        logger.debug("Game state reset on screen entry")

        # Schedule update
        # schedule_interval is available on pyglet.clock module
        pyglet.clock.schedule_interval(self.update, 1 / CONFIG.TARGET_FPS)

    def on_exit(self) -> None:
        """Called when game running screen is left."""
        logger.debug("Game running screen exited")
        self.music_player.pause()
        # unschedule is available on pyglet.clock module
        pyglet.clock.unschedule(self.update)

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
            self.mouse.reset(
                self.window.width * CONFIG.MOUSE_START_X_RATIO,
                self.window.height * CONFIG.MOUSE_START_Y_RATIO,
            )
            self.kitten.reset(
                self.window.width * CONFIG.KITTEN_START_X_RATIO,
                self.window.height * CONFIG.KITTEN_START_Y_RATIO,
            )
            self.elapsed_time = 0.0
            self.game_over = False
            logger.debug("Game state reset complete")

        if self.game_over:
            return

        # Manual Movement Control (Sets Velocity)
        base_speed = self.window.width / CONFIG.WINDOW_TRAVERSAL_TIME
        if symbol == key.UP:
            self.mouse.velocity_x = 0.0
            self.mouse.velocity_y = base_speed
        elif symbol == key.DOWN:
            self.mouse.velocity_x = 0.0
            self.mouse.velocity_y = -base_speed
        elif symbol == key.LEFT:
            self.mouse.velocity_x = -base_speed
            self.mouse.velocity_y = 0.0
        elif symbol == key.RIGHT:
            self.mouse.velocity_x = base_speed
            self.mouse.velocity_y = 0.0
        # Diagonals
        elif symbol == key.HOME:  # Up-Left
            self.mouse.velocity_x = -base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
            self.mouse.velocity_y = base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.PAGEUP:  # Up-Right
            self.mouse.velocity_x = base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
            self.mouse.velocity_y = base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.END:  # Down-Left
            self.mouse.velocity_x = -base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
            self.mouse.velocity_y = -base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.PAGEDOWN:  # Down-Right
            self.mouse.velocity_x = base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
            self.mouse.velocity_y = -base_speed * CONFIG.DIAGONAL_MOVEMENT_FACTOR
        elif symbol == key.SPACE:  # Stop
            self.mouse.velocity_x = 0.0
            self.mouse.velocity_y = 0.0

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
            self.mouse.set_velocity_to_target(float(x), float(y))

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

    def _update_entities(self, dt: float) -> float:
        """Update mouse and kitten positions.

        Args:
            dt: Time elapsed since last update in seconds.

        Returns:
            Distance between mouse and kitten.
        """
        # Update mouse position
        self.mouse.update(dt, self.window.width, self.window.height)

        # Update kitten position (chases mouse)
        is_moving = self.kitten.chase_target(self.mouse.center_x, self.mouse.center_y)
        self.kitten.clamp_to_bounds(self.window.width, self.window.height)

        # Check if kitten stopped moving
        if self.kitten.was_moving and not is_moving and self.meow_sound:
            _ = self.meow_sound.play()  # Discard return value

        # Calculate distance between characters
        distance = self.kitten.distance_to(self.mouse.center_x, self.mouse.center_y)
        return distance

    def _update_health_stamina(self, distance: float, dt: float) -> None:
        """Update health and stamina based on proximity and time.

        Args:
            distance: Current distance between kitten and mouse.
            dt: Time elapsed since last update in seconds.
        """
        # Drain/Regen if within range
        if distance < self.catch_range:
            proximity_factor = 1.0 - (distance / self.catch_range)
            proximity_factor = max(0.0, min(1.0, proximity_factor))

            transfer_amount = (CONFIG.BASE_DRAIN_RATE * proximity_factor) * dt

            self.mouse.health -= transfer_amount
            self.kitten.stamina += transfer_amount

        # Passive Stamina Drain
        self.kitten.stamina -= CONFIG.PASSIVE_STAMINA_DRAIN * dt

        # Clamp values
        self.mouse.health = max(0.0, min(CONFIG.MAX_HEALTH, self.mouse.health))
        self.kitten.stamina = max(0.0, min(CONFIG.MAX_STAMINA, self.kitten.stamina))

    def _check_win_loss_conditions(self) -> None:
        """Check and handle win/loss game conditions."""
        if self.mouse.health <= 0:
            self.game_over = True
            self.mouse.velocity_x = 0.0
            self.mouse.velocity_y = 0.0
            logger.info("Game Over: Mouse caught by kitten")
            self._transition_to_game_end(is_win=False)

        elif self.kitten.stamina <= 0:
            self.game_over = True
            self.mouse.velocity_x = 0.0
            self.mouse.velocity_y = 0.0
            logger.info("Game Over: Kitten exhausted, player wins")
            self._transition_to_game_end(is_win=True)

    def _transition_to_game_end(self, is_win: bool) -> None:
        """Transition to the game end screen.

        Args:
            is_win: True if player won, False if player lost.
        """
        from ..screen_manager import ScreenManager
        from .game_end import GameEndScreen

        manager = getattr(self.window, "_screen_manager", None)
        if isinstance(manager, ScreenManager):
            game_end_screen = manager.screens.get("game_end")
            if isinstance(game_end_screen, GameEndScreen):
                # Set outcome on the game end screen
                game_end_screen.set_outcome(is_win, self.elapsed_time, self.mouse.total_distance)
            manager.set_active_screen("game_end")

    def _update_ui_bars(self) -> None:
        """Update health and stamina bar positions and values."""
        # Mouse Bar (centered above sprite)
        self.mouse_bar_bg.x = self.mouse.center_x - (CONFIG.BAR_WIDTH / 2)
        self.mouse_bar_bg.y = self.mouse.center_y + (self.mouse.height / 2) + CONFIG.BAR_OFFSET
        self.mouse_bar_fg.x = self.mouse_bar_bg.x
        self.mouse_bar_fg.y = self.mouse_bar_bg.y
        self.mouse_bar_fg.width = CONFIG.BAR_WIDTH * (self.mouse.health / CONFIG.MAX_HEALTH)
        self.mouse_bar_fg.color = (
            CONFIG.COLOR_GREEN
            if self.mouse.health > CONFIG.LOW_HEALTH_THRESHOLD
            else CONFIG.COLOR_RED
        )

        # Kitten Bar (centered above sprite)
        self.kitten_bar_bg.x = self.kitten.center_x - (CONFIG.BAR_WIDTH / 2)
        self.kitten_bar_bg.y = self.kitten.center_y + (self.kitten.height / 2) + CONFIG.BAR_OFFSET
        self.kitten_bar_fg.x = self.kitten_bar_bg.x
        self.kitten_bar_fg.y = self.kitten_bar_bg.y
        self.kitten_bar_fg.width = CONFIG.BAR_WIDTH * (self.kitten.stamina / CONFIG.MAX_STAMINA)
        self.kitten_bar_fg.color = (
            CONFIG.COLOR_GREEN
            if self.kitten.stamina > CONFIG.LOW_HEALTH_THRESHOLD
            else CONFIG.COLOR_RED
        )

    def update(self, dt: float) -> None:
        """Update game running screen state.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        if self.game_over:
            return

        # Track elapsed time
        self.elapsed_time += dt

        distance = self._update_entities(dt)
        self._update_health_stamina(distance, dt)
        self._check_win_loss_conditions()
        self._update_ui_bars()

    def draw(self) -> None:
        """Render game running screen content."""
        # Draw entities
        self.kitten.draw()
        self.mouse.draw()

        # Draw UI
        self.mouse_bar_bg.draw()
        self.mouse_bar_fg.draw()
        self.kitten_bar_bg.draw()
        self.kitten_bar_fg.draw()
