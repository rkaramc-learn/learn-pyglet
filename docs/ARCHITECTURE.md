# Architecture

`chaser-game` is a Python-based interactive desktop application built with `pyglet`. It implements a modular entity-component architecture with screen-based state management.

## High-Level Overview

The application uses a screen-based game loop with:

- **Screen Manager** for screen transitions and lifecycle
- **Entity System** for game objects (Kitten, Mouse)
- **Game Mechanics** for decoupled game logic (input, collision, health)
- **Centralized Configuration** via frozen dataclass

## Application Flow

1. **Entry Point:** `src/chaser_game/__init__.py` exposes `main()` which parses CLI arguments, initializes logging, and calls `run_hello_world()`.
2. **Initialization:** `src/chaser_game/hello_world.py` creates the `pyglet.window.Window`, sets up the `ScreenManager`, registers all screens, and starts the game loop.
3. **Screen Flow:**
   - `SplashScreen` → `GameStartScreen` → `GameRunningScreen` → `GameEndScreen`
4. **Game Loop (60Hz):**
   - **Update:** `ScreenManager.update(dt)` delegates to the active screen
   - **Render:** `ScreenManager.draw()` renders the active screen
   - **Input:** Key/mouse events routed through `ScreenManager` to active screen

## Core Modules

| Module         | Path                | Responsibility                                  |
| -------------- | ------------------- | ----------------------------------------------- |
| Entry Point    | `__init__.py`       | CLI args, logging, app bootstrap                |
| Game Loop      | `hello_world.py`    | Window, screen setup, pyglet event loop         |
| Screen Manager | `screen_manager.py` | Screen registration, transitions, event routing |
| Game State     | `game_state.py`     | State machine (PLAYING, PAUSED, WIN, LOSE)      |
| Configuration  | `config.py`         | Frozen dataclass with all game constants        |

## Entity System

Located in `src/chaser_game/entities/`:

| Entity      | File           | Description                                                                       |
| ----------- | -------------- | --------------------------------------------------------------------------------- |
| `Entity`    | `base.py`      | Base dataclass with position, velocity, state                                     |
| `Character` | `character.py` | Extended entity with health, stamina, sprite                                      |
| `Kitten`    | `kitten.py`    | AI-controlled chaser with stamina; exhausts when stamina depletes (win condition) |
| `Mouse`     | `mouse.py`     | Player-controlled entity with health; dies when caught (lose condition)           |

### Entity States (`EntityState`)

- `IDLE` - Not moving
- `MOVING` - Active movement (player input)
- `CHASING` - AI chasing a target

## Game Mechanics

Located in `src/chaser_game/mechanics/`:

| System    | File           | Responsibility                              |
| --------- | -------------- | ------------------------------------------- |
| Input     | `input.py`     | Keyboard state handling, movement direction |
| Collision | `collision.py` | Boundary clamping, entity interactions      |
| Health    | `health.py`    | Health/stamina drain, win/lose conditions   |

## Screens

Located in `src/chaser_game/screens/`:

| Screen              | File              | Description                            |
| ------------------- | ----------------- | -------------------------------------- |
| `ScreenProtocol`    | `base.py`         | Protocol with window lifecycle methods |
| `SplashScreen`      | `splash.py`       | Initial branding/loading screen        |
| `GameStartScreen`   | `game_start.py`   | Start menu, instructions               |
| `GameRunningScreen` | `game_running.py` | Main gameplay loop                     |
| `GameEndScreen`     | `game_end.py`     | Win/lose display, restart option       |

### Screen Lifecycle

- `on_enter()` - Called when screen becomes active
- `on_exit()` - Called when leaving screen
- `update(dt)` - Per-frame logic
- `draw()` - Render content
- `on_key_press()`, `on_mouse_press()` - Input handling

## UI Components

Located in `src/chaser_game/ui/`:

| Component  | File            | Description                   |
| ---------- | --------------- | ----------------------------- |
| Health Bar | `health_bar.py` | Visual health/stamina display |

## Assets

| Type               | Path                              | Tracking            |
| ------------------ | --------------------------------- | ------------------- |
| Kitten sprite      | `assets/images/kitten.png`        | Tracked             |
| Meow sound         | `assets/audio/sfx/meow.wav`       | Tracked             |
| Mouse sprite sheet | `assets/sprites/mouse_sheet.png`  | Ignored (generated) |
| Ambience music     | `assets/audio/music/ambience.wav` | Ignored (large)     |

## Configuration

All constants are centralized in `config.py` as a frozen `GameConfig` dataclass:

- Window dimensions and FPS
- Sprite scales and animation rates
- Movement speeds and thresholds
- Health/stamina values
- Asset paths
- UI dimensions and colors

## Supporting Modules

| Module           | File                  | Responsibility                        |
| ---------------- | --------------------- | ------------------------------------- |
| Types            | `types.py`            | Protocol definitions, type aliases    |
| Assets           | `assets.py`           | Asset loading and caching             |
| Asset Manifest   | `asset_manifest.py`   | Asset metadata and validation         |
| Movement         | `movement.py`         | Movement calculations, lerp utilities |
| Sprite Generator | `sprite_generator.py` | Generate sprite sheets from video     |
| Restore Assets   | `restore_assets.py`   | Asset recovery/regeneration           |
| Logging          | `logging_config.py`   | Logging setup with TRACE level        |
