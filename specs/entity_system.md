# Entity System Refactoring Specification

> [!NOTE] > **Status: IMPLEMENTED** (pyglet-ciz epic)
> This document reflects the actual implementation of the entity system refactoring.

## Overview

Refactor `hello_world.py` from a monolithic function into a modular entity-component architecture using `ScreenManager`, specific `mechanics` systems, and class-based entities.

## Problem Statement

Original implementation had:

- **God Function**: 294-line `run_hello_world()` containing all logic
- **No Entity Abstraction**: Mouse/Kitten represented as loose variables
- **Excessive Closures**: 6+ mutable variables shared via `nonlocal`
- **Magic Numbers**: Hardcoded values scattered throughout
- **Mixed Responsibilities**: Update function handles physics, AI, health, UI, win conditions

## Implemented Architecture

```tree
src/chaser_game/
├── hello_world.py       # Entry point runner
├── screen_manager.py    # Screen management and transition logic
├── config.py            # Constants: speeds, health, asset paths
├── entities/
│   └── character.py     # Character base class and Key/Mouse implementations
├── mechanics/
│   ├── health.py        # Health/stamina calculation logic
│   ├── collision.py     # Bounds checking logic
│   └── input.py         # Input handling logic
├── screens/
│   ├── base.py          # Screen protocol/base
│   ├── splash.py        # Intro screen
│   ├── game_start.py    # Menu screen
│   ├── game_running.py  # Main gameplay loop
│   └── game_end.py      # Result screen
└── ui/
    └── health_bar.py    # Health bar component
```

## Entity Classes

`src/chaser_game/entities/character.py`:

- **Character**: Base class with center-based positioning (`center_x`, `center_y`), bounds clamping, and velocity-based movement.
- **Mouse**: Player character, inherits from `Character`. Handles distance tracking and sprite rendering.
- **Kitten**: AI character, inherits from `Character`. Implements chase logic.

## Configuration Module

`src/chaser_game/config.py`:
Centralized configuration `GameConfig` dataclass containing:

- Window settings
- Movement speeds and physics constants
- Health/Stamina parameters
- UI dimensions
- Asset paths

## Game State Management

- **ScreenManager**: Manages high-level app state (Splash -> Start -> Running -> End).
- **GameStateManager**: (Internal to GameRunning) Tracks Win/Loss conditions during gameplay.
- **GameRunningScreen**: Orchestrates the game loop, integrating entities, mechanics, and UI.

## Systems (Mechanics)

Logic separated into functional modules in `mechanics/`:

- `health.py`: `update_health_stamina()` function.
- `collision.py`: `check_bounds()` (integrated into Character methods).
- `input.py`: Input processing utilities.

## Verification Plan

1. **Type Safety**: `uv run basedpyright` passes.
2. **Manual Testing**: Game runs correctly through all screens.
3. **Unit Tests**: Coverage exists for new components.
