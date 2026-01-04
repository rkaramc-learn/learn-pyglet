# AGENTS.md

## Project Overview
`pyglet-readme` is a Python-based interactive desktop application built using the `pyglet` library. It demonstrates fundamental 2D game development concepts including sprite rendering, continuous movement logic (keyboard and mouse), collision handling (basic window bounds), and audio playback (sound effects and looped background music).

## Architecture
The application follows a standard single-window 2D game loop architecture:
1.  **Entry Point:** `src/pyglet_readme/__init__.py` exposes the `main` entry point which calls `run_hello_world`.
2.  **Initialization:** `src/pyglet_readme/hello_world.py` sets up the `pyglet.window.Window`, loads resources (images/audio), and initializes state variables.
3.  **Input Handling:**
    *   **Keyboard:** `pyglet.window.key.KeyStateHandler` tracks key states for continuous smooth movement.
    *   **Mouse:** Event handlers (`on_mouse_press`) capture point-and-click targeting.
4.  **Game Loop:**
    *   **Update:** A scheduled function (`update(dt)`) runs at 60Hz to calculate position changes based on input and `dt` (delta time).
    *   **Render:** The `on_draw` event clears the screen and draws the label and sprite at updated coordinates.

## Core Components
*   **`src/pyglet_readme/hello_world.py`**: Contains the bulk of the application logic.
    *   `run_hello_world()`: Main setup and execution function.
    *   `update(dt)`: Handles movement physics and boundary checking.
    *   `on_draw()`: Handles rendering.
*   **Assets**:
    *   `kitten.png`: The player sprite.
    *   `meow.wav`: Sound effect triggered on stop.
    *   `ambience.wav`: Background music loop.

## Dependencies
*   **Runtime:**
    *   `pyglet >= 2.1.11`: The core multimedia library.
    *   `python >= 3.13`: The execution environment.
*   **Development:**
    *   `basedpyright >= 1.37.0`: Static type checker (Strict).
*   **Package Manager:**
    *   `uv`: Used for dependency resolution, environment management, and script execution.

## Development Workflow
1.  **Version Control:** The project uses `jj` (Jujutsu).
    *   Create revisions: `jj new`
    *   Commit changes: `jj commit -m "message"`
    *   **Note:** Large binary files (>1MB) should ideally be avoided in VCS history.
2.  **Running:**
    *   `uv run pyglet-readme`
3.  **Testing/Verification:**
    *   Manual verification by running the app.
    *   Static analysis: `uv run basedpyright` (MUST pass before completion).

## Coding Standards
*   **Type Safety:** All code must be fully type-hinted. `basedpyright` is the authority.
*   **Style:** PEP 8 compliance.
*   **Structure:** Follow the `src` layout pattern.
*   **Resources:** Use `pyglet.resource` for loading assets relative to the script directory.

## Environment Setup
1.  **Prerequisites:** Install `uv` (https://github.com/astral-sh/uv).
2.  **Installation:**
    ```powershell
    uv sync
    ```
3.  **Execution:**
    ```powershell
    uv run pyglet-readme
    ```

## Operational Guidelines for Agents
*   **Asset Management:** Do not blindly create or commit large binary assets. Check file sizes.
*   **Tool Usage:**
    *   Use `search_file_content` for code discovery.
    *   Use `read_file` to verify file content before editing.
    *   Always verify changes with `uv run basedpyright`.
*   **Safety:**
    *   Explain any file deletion or shell commands that modify the system state outside the project directory.
