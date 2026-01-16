"""Color definitions and types.

This module defines the structured Color type used throughout the application
to ensure type safety and consistency in color handling.
"""

from typing import NamedTuple


class Color(NamedTuple):
    """RGB color tuple with named components.

    Compatible with pyglet's tuple expectation (r, g, b).
    Alpha channel is optional in pyglet, but here we strictly define RGB.
    If RGBA is needed, a separate type should be defined.
    """

    r: int
    g: int
    b: int
