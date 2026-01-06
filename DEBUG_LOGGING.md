# Debug Logging Guide

The game now includes comprehensive logging with multiple log levels and flexible output options.

## Log Levels

### INFO (Default)
Shows key events and state changes. Good for understanding game flow.

```bash
uv run pyglet-readme
```

### DEBUG (Verbose Mode)
Shows detailed information about asset loading, paths, performance metrics, and more.

```bash
uv run pyglet-readme --verbose
# or
uv run pyglet-readme -v
```

## File Logging

Write logs to a file for later analysis:

```bash
uv run pyglet-readme --log-file=game.log
```

Combine with verbose mode:

```bash
uv run pyglet-readme --verbose --log-file=debug.log
```

## What Gets Logged

### Assets Module
- **DEBUG**: Asset directory paths, individual asset verification, load times
- **INFO**: AssetLoader initialization, all assets verified
- **WARNING**: Missing assets
- **ERROR**: Asset loading failures

### Game Module (hello_world.py)
- **DEBUG**: Entity creation, sprite details, movement speeds
- **INFO**: Game state changes, initialization milestones
- **WARNING**: Asset fallbacks being used
- **ERROR**: Critical failures

### Test Module (test_startup.py)
- **DEBUG**: Detailed test execution steps
- **INFO**: Test results and progress
- **ERROR**: Test failures

## Example Output

### INFO Level (Default)
```
INFO     | __main__ | Starting pyglet-readme application
INFO     | pyglet_readme.hello_world | Starting game initialization
INFO     | pyglet_readme.hello_world | Creating game window
INFO     | pyglet_readme.hello_world | Window created: 1280x720
INFO     | pyglet_readme.hello_world | Game initialization complete, starting game loop
```

### DEBUG Level (--verbose)
```
INFO     | __main__ | Starting pyglet-readme application
DEBUG    | __main__ | Verbose mode enabled
DEBUG    | pyglet_readme.assets | Initializing AssetLoader
DEBUG    | pyglet_readme.assets | Assets directory: src/pyglet_readme/assets
DEBUG    | pyglet_readme.assets | Images directory: src/pyglet_readme/assets/images
DEBUG    | pyglet_readme.assets | Sprites directory: src/pyglet_readme/assets/sprites
DEBUG    | pyglet_readme.assets | SFX directory: src/pyglet_readme/assets/audio/sfx
DEBUG    | pyglet_readme.assets | Music directory: src/pyglet_readme/assets/audio/music
INFO     | pyglet_readme.assets | AssetLoader initialized successfully
INFO     | pyglet_readme.hello_world | Starting game initialization
DEBUG    | pyglet_readme.hello_world | Asset loader initialized
DEBUG    | pyglet_readme.hello_world | Loading kitten sprite
DEBUG    | pyglet_readme.assets | Loading image: assets/images/kitten.png
DEBUG    | pyglet_readme.assets | Image loaded successfully in 0.039s: assets/images/kitten.png (1024x1024)
DEBUG    | pyglet_readme.hello_world | Kitten sprite loaded: 1024x1024, position: (640, 360)
INFO     | pyglet_readme.hello_world | Creating game window
INFO     | pyglet_readme.hello_world | Window created: 1280x720
```

## Log Format

Logs are formatted as:
```
LEVEL    | module.name | message
```

For file output, timestamps are included:
```
2024-01-06 14:30:45,123 | LEVEL    | module.name | message
```

## Running Tests with Debug Logging

Run the E2E test suite with verbose logging:

```bash
uv run python test_startup.py --verbose
```

This shows:
- Asset system initialization
- Asset verification results
- Game window creation
- Sprite and sound loading
- Test execution flow

## Demo Scripts

See the logging system in action:

```bash
# Show all asset loads with timestamps and performance metrics
uv run python demo_debug_logging.py

# Compare INFO vs DEBUG levels side-by-side
uv run python demo_log_levels.py
```

## Performance Monitoring

Debug logging includes performance metrics:
- Image load time: `Image loaded successfully in 0.039s`
- Sound load time: `Sound loaded successfully in 0.001s`

Use this to identify performance bottlenecks during development.

## Integration with Your IDE

Many IDEs can parse the log output and highlight errors/warnings:
- Red for ERROR
- Yellow for WARNING
- Blue for DEBUG
- Green for INFO

When using `--log-file`, you can open the log in your editor for easier navigation.
