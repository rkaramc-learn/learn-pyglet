# Debug Logging Guide

The game now includes comprehensive logging with multiple verbosity levels and flexible output options.

## Verbosity Levels

### WARN (Default)
Only warnings and errors. Minimal output.

```bash
uv run pyglet-readme
```

### INFO (-v)
Shows key events and state changes. Good for understanding game flow.

```bash
uv run pyglet-readme -v
# or
uv run pyglet-readme --verbose
```

### DEBUG (-vv)
Shows detailed information about asset loading, paths, performance metrics, and more.

```bash
uv run pyglet-readme -vv
```

### TRACE (-vvv)
Ultra-detailed system information. Everything gets logged.

```bash
uv run pyglet-readme -vvv
```

## File Logging

Write logs to a file for later analysis:

```bash
uv run pyglet-readme --log-file=game.log
```

Combine with verbosity levels:

```bash
uv run pyglet-readme -v --log-file=info.log      # INFO level to file
uv run pyglet-readme -vv --log-file=debug.log    # DEBUG level to file
uv run pyglet-readme -vvv --log-file=trace.log   # TRACE level to file
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

### WARN Level (Default)
Only errors and warnings:
```
WARNING  | __main__ | Starting pyglet-readme application
```

### INFO Level (-v)
Key milestones:
```
WARNING  | __main__ | Starting pyglet-readme application
INFO     | chaser_game.hello_world | Starting game initialization
INFO     | chaser_game.hello_world | Creating game window
INFO     | chaser_game.hello_world | Window created: 1280x720
INFO     | chaser_game.hello_world | Game initialization complete, starting game loop
```

### DEBUG Level (-vv)
Detailed flow and asset information:
```
WARNING  | __main__ | Starting pyglet-readme application
INFO     | chaser_game.hello_world | Starting game initialization
DEBUG    | chaser_game.assets | Initializing AssetLoader
DEBUG    | chaser_game.assets | Assets directory: src/chaser_game/assets
DEBUG    | chaser_game.assets | Loading image: assets/images/kitten.png
DEBUG    | chaser_game.assets | Image loaded successfully in 0.039s: assets/images/kitten.png (1024x1024)
DEBUG    | chaser_game.hello_world | Kitten sprite loaded: 1024x1024, position: (640, 360)
INFO     | chaser_game.hello_world | Creating game window
INFO     | chaser_game.hello_world | Window created: 1280x720
```

### TRACE Level (-vvv)
Ultra-detailed system information:
```
WARNING  | __main__ | Starting pyglet-readme application
TRACE    | chaser_game.assets | Asset paths and system details
DEBUG    | chaser_game.assets | All debug messages
... (everything)
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
