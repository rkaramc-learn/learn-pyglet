import pyglet

from ..assets import get_loader
from ..config import CONFIG


class ChaserLogo:
    """Reusable component for the Chaser Game logo with accents.

    Renders the SVG logo asset as a sprite.
    """

    def __init__(self, x: float, y: float, scale: float = 1.0, batch=None, group=None):
        self.x = x
        self.y = y
        self.scale = scale
        self.batch = batch
        self.group = group

        # Load SVG/Image
        try:
            loader = get_loader()
            logo_image = loader.load_image(CONFIG.ASSET_LOGO_SVG)
            # Center anchor
            logo_image.anchor_x = logo_image.width // 2
            logo_image.anchor_y = logo_image.height // 2

            self.sprite = pyglet.sprite.Sprite(logo_image, x=x, y=y, batch=batch, group=group)
            self.sprite.scale = scale
        except Exception as e:
            # Fallback if SVG fails to load (e.g. missing decoder)
            print(f"Failed to load SVG logo: {e}")
            self.sprite = None
            # Fallback text
            self.label = pyglet.text.Label(
                "CHASER",
                font_name=CONFIG.FONT_NAME,
                font_size=CONFIG.FONT_SIZE_HERO,
                color=(*CONFIG.COLOR_TEXT, 255),
                x=x,
                y=y,
                anchor_y="center",
                batch=batch,
                group=group,
                bold=True,  # pyright: ignore[reportCallIssue]
            )

    def update_position(self, x: float, y: float) -> None:
        """Update logo position.

        Args:
            x: New x coordinate.
            y: New y coordinate.
        """
        self.x = x
        self.y = y
        if self.sprite:
            self.sprite.x = x
            self.sprite.y = y
        elif hasattr(self, "label"):
            self.label.x = x
            self.label.y = y

    def update_opacity(self, opacity: int) -> None:
        """Update logo opacity.

        Args:
            opacity: New opacity (0-255).
        """
        if self.sprite:
            self.sprite.opacity = opacity
        elif hasattr(self, "label"):
            # Text uses 4th component of color for opacity, but pyglet.text.Label
            # usually has an opacity property too (or batch handles it).
            # Direct color update is safer for standalone label.
            # However, label.opacity is available in recent pyglet versions.
            try:
                self.label.opacity = opacity
            except AttributeError:
                # Fallback for older pyglet or if opacity not exposed
                current = self.label.color
                self.label.color = (current[0], current[1], current[2], opacity)

    def draw(self):
        """Draw the logo components."""
        if self.batch is None:
            if self.sprite:
                self.sprite.draw()
            elif hasattr(self, "label"):
                self.label.draw()
