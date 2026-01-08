# Testing Strategy

This document outlines the testing strategies for `chaser-game`, a pyglet-based game.

## Strategy Overview

| Strategy                     | Status                 | Description                        |
| ---------------------------- | ---------------------- | ---------------------------------- |
| Unit Tests                   | ✅ IMPLEMENTED         | Test game logic in isolation       |
| Integration Tests (Mocked)   | ✅ IMPLEMENTED         | Test with mocked pyglet components |
| Integration Tests (Headless) | 🔄 UNDER CONSIDERATION | Test with headless pyglet window   |
| Snapshot/Regression Testing  | 🔄 UNDER CONSIDERATION | Compare rendered frames            |
| Automated Gameplay Tests     | 🔄 UNDER CONSIDERATION | Script input sequences             |

---

## ✅ Unit Tests (IMPLEMENTED)

Test game logic in isolation without creating a pyglet window.

### Testable Components

| Component           | Test File                   | Coverage                    |
| ------------------- | --------------------------- | --------------------------- |
| `Entity` base class | `test_entity_base.py`       | Position, velocity, state   |
| `Kitten` entity     | `test_entity_kitten.py`     | Chase logic, stamina        |
| `Mouse` entity      | `test_entity_mouse.py`      | Movement, health            |
| `GameStateManager`  | `test_game_state.py`        | State transitions           |
| `GameConfig`        | `test_config.py`            | Configuration values        |
| Movement utilities  | `test_movement.py`          | Vector math, lerp, distance |
| Input system        | `test_systems_input.py`     | Keyboard handling           |
| Collision system    | `test_systems_collision.py` | Boundary clamping           |
| Health system       | `test_systems_health.py`    | Health/stamina drain        |
| UI Health Bar       | `test_ui_health_bar.py`     | Bar rendering logic         |
| Asset Manifest      | `test_asset_manifest.py`    | YAML parsing, validation    |
| Asset Loader        | `test_assets.py`            | Path resolution, caching    |
| Logging             | `test_logging.py`           | Log configuration           |

### Example

```python
def test_kitten_stamina_drain():
    kitten = Kitten()
    kitten.apply_stamina_change(-20)
    assert kitten.stamina == 80.0

def test_mouse_health_clamps_to_zero():
    mouse = Mouse()
    mouse.apply_health_change(-200)
    assert mouse.health == 0.0
```

---

## ✅ Integration Tests with Mocking (IMPLEMENTED)

Test game initialization and asset loading by mocking pyglet components.

### Test Files

| Test File                               | Coverage                                    |
| --------------------------------------- | ------------------------------------------- |
| `test_e2e_game_startup.py`              | Full game initialization with mocked window |
| `test_hello_world_assets.py`            | Asset loading and configuration             |
| `test_startup.py`                       | Module import verification                  |
| `test_sprite_generation_integration.py` | Sprite sheet generation flow                |

### Mocking Approach

```python
@patch("pyglet.app.run")
@patch("pyglet.window.Window")
@patch("pyglet.sprite.Sprite")
@patch("pyglet.resource.image")
@patch("pyglet.resource.media")
def test_game_startup_asset_loading_calls(
    self, mock_media, mock_image, mock_sprite, mock_window_class, mock_app_run
):
    mock_window = MagicMock()
    mock_window.width = 800
    mock_window.height = 600
    mock_window_class.return_value = mock_window
    # ... test asset loading
```

---

## 🔄 Integration Tests with Headless Window (UNDER CONSIDERATION)

Create a headless pyglet window for testing screens and rendering logic without a display.

### Approach

```python
import pyglet
pyglet.options['headless'] = True  # Must set before importing window

def test_screen_manager_transitions():
    window = pyglet.window.Window(800, 600)
    manager = ScreenManager(window)
    manager.register_screen("splash", SplashScreen(window))
    manager.set_active_screen("splash")
    assert manager.active_screen_name == "splash"
    window.close()
```

### Benefits

- Tests actual pyglet rendering pipeline
- Validates OpenGL context creation
- Tests screen lifecycle without mocking

### Limitations

- Requires OpenGL drivers (may fail in some CI environments)
- Slower than unit tests

---

## 🔄 Snapshot/Regression Testing (UNDER CONSIDERATION)

Capture rendered frames and compare against baseline images.

**_Approach_**

```python
def test_game_start_screen_renders_correctly():
    pyglet.options['headless'] = True
    window = pyglet.window.Window(800, 600)
    screen = GameStartScreen(window)
    screen.on_enter()
    screen.draw()

    # Capture frame
    buffer = pyglet.image.get_buffer_manager().get_color_buffer()
    buffer.save('current.png')

    # Compare with baseline
    assert images_match('baseline/game_start.png', 'current.png')
    window.close()
```

**_Benefits_**

- Catches visual regressions
- Documents expected UI appearance

**_Limitations_**

- Baseline images need maintenance
- Platform-specific rendering differences
- Large storage requirements

---

## 🔄 Automated Gameplay Tests (UNDER CONSIDERATION)

Script input sequences and verify game state transitions.

**_Approach_**

```python
def test_mouse_escapes_kitten_for_win():
    game = create_test_game()

    # Simulate keyboard input for 10 seconds
    for _ in range(600):  # 60 FPS * 10 seconds
        game.simulate_key_held(pyglet.window.key.RIGHT)
        game.update(1/60)

    # Verify kitten stamina depleted
    assert game.kitten.stamina == 0
    assert game.state_manager.is_player_won()

def test_kitten_catches_mouse_for_loss():
    game = create_test_game()

    # Mouse stands still, kitten catches up
    for _ in range(300):
        game.update(1/60)

    # Verify mouse health depleted
    assert game.mouse.health == 0
    assert game.state_manager.is_player_lost()
```

**_Benefits_**

- Tests actual gameplay scenarios
- Validates win/lose conditions
- Regression tests for game balance

**_Limitations_**

- Requires deterministic game loop
- Complex setup and teardown
- Potentially slow

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=chaser_game

# Run specific test file
uv run pytest tests/test_entity_kitten.py

# Run with verbose output
uv run pytest -v
```

### Current Test Structure

```text
tests/
├── test_asset_manifest.py      # Asset manifest parsing
├── test_asset_structure.py     # Asset directory structure
├── test_assets.py              # Asset loader
├── test_config.py              # GameConfig values
├── test_e2e_game_startup.py    # E2E with mocking
├── test_entity_base.py         # Entity base class
├── test_entity_kitten.py       # Kitten entity
├── test_entity_mouse.py        # Mouse entity
├── test_game_state.py          # GameStateManager
├── test_hello_world_assets.py  # Asset integration
├── test_logging.py             # Logging configuration
├── test_movement.py            # Movement utilities
├── test_sprite_generation_integration.py
├── test_sprite_generator.py    # Sprite sheet generation
├── test_startup.py             # Module imports
├── test_systems_collision.py   # Collision mechanics
├── test_systems_health.py      # Health mechanics
├── test_systems_input.py       # Input mechanics
└── test_ui_health_bar.py       # Health bar UI
```
