# AGENTS.md

## Project Overview

`pyglet-readme` is a Python-based interactive desktop application built using the `pyglet` library. It demonstrates fundamental 2D game development concepts including sprite rendering, continuous movement logic (keyboard and mouse), collision handling (basic window bounds), and audio playback (sound effects and looped background music).

**Recent Features:**

- Sprite sheet animation (mouse sprite).
- Simple AI: Kitten automatically chases the mouse sprite when idle.
- Linear Interpolation (Lerp) for smooth mouse movement.

## Architecture

The application follows a standard single-window 2D game loop architecture:

1. **Entry Point:** `src/pyglet_readme/__init__.py` exposes the `main` entry point which calls `run_hello_world`.
2. **Initialization:** `src/pyglet_readme/hello_world.py` sets up the `pyglet.window.Window`, loads resources (images/audio), and initializes state variables.
3. **Input Handling:**
   - **Keyboard:** `pyglet.window.key.KeyStateHandler` tracks key states for continuous smooth movement.
   - **Mouse:** Event handlers (`on_mouse_press`) trigger the mouse sprite's movement to the clicked location.
4. **Game Loop:**
   - **Update:** A scheduled function (`update(dt)`) runs at 60Hz. It handles:
     - Kitten movement (keyboard input OR automatic mouse-chasing behavior).
     - Mouse sprite movement (tweening).
   - **Render:** The `on_draw` event clears the screen and draws the label and sprites at updated coordinates.

## Core Components

- **`src/pyglet_readme/hello_world.py`**: Contains the bulk of the application logic.
- **Assets**:
  - `kitten.png`: The player sprite (Tracked).
  - `meow.wav`: Sound effect triggered on stop (Tracked).
  - **Ignored/Local Assets:** (Ensure these exist locally for full functionality)
    - `ambience.wav`: Background music loop (Ignored to save space).
    - `mouse_sheet.png`: Animated sprite sheet generated from `mouse.mp4` (Ignored).
    - `mouse.mp4`: Source video (Ignored).

## Dependencies

- **Runtime:**
  - `pyglet >= 2.1.11`: The core multimedia library.
  - `python >= 3.13`: The execution environment.
- **Development:**
  - `basedpyright >= 1.37.0`: Static type checker (Strict).
  - `ruff >= 0.14.10`: Code formatter and linter (Strict).
- **Package Manager:**
  - `uv`: Used for dependency resolution, environment management, and script execution.
- **External Tools:**
  - `ffmpeg`: Used for media conversion (e.g. creating sprite sheets).
  - `bd` (Beads): Issue tracker/memory tool.
  - `specify` (GitHub Spec Kit): Specification tool for AI agents.

## Development Workflow

1. **Version Control:** The project uses `jj` (Jujutsu).
   - **Save Work:** Use `jj commit -m "message"` as the primary way to save changes. It is more efficient than `jj describe` followed by `jj new` as it performs both in one tool call.
   - **Untracking Files:** Use `jj file untrack <path>` to stop tracking a file without deleting it.
   - **Listing Files:** Use `jj file list` (add `--no-pager` for full output in non-interactive shells).
   - **Note:** Large binary files (>1MB) are strictly ignored via `.gitignore`.
2. **Running:**
   - `uv run pyglet-readme`
3. **Testing/Verification:**
   - Manual verification by running the app.
   - Static analysis: `uv run basedpyright` (MUST pass before completion).

## Coding Standards

- **Type Safety:** All code must be fully type-hinted. `basedpyright` is the authority.
- **Style:** PEP 8 compliance.
- **Structure:** Follow the `src` layout pattern.
- **Resources:** Use `pyglet.resource` for loading assets relative to the script directory.

## Environment Setup

1. **Prerequisites:** Install `uv` (<https://github.com/astral-sh/uv>).
2. **Installation:**

   ```powershell
   uv sync
   ```

3. **Execution:**

   ```powershell
   uv run pyglet-readme
   ```

## Operational Guidelines for Agents

- **Asset Management:** Do not blindly create or commit large binary assets. Check file sizes.
  - If creating derived assets (like sprite sheets), verify they are added to `.gitignore`.
- **Environment & Shell Awareness:**
  - **Check OS:** Identify the operating system (`win32`, `linux`, `darwin`) before running commands.
  - **Windows:** The shell is **PowerShell**.
    - Use `Get-ChildItem -Force` instead of `ls -a`.
    - Use `Invoke-WebRequest -Uri <url> -OutFile <path>` instead of `curl` or `wget`.
  - **Linux/macOS:** Use standard `bash`/`sh` commands (e.g., `ls -a`, `curl`).
- **Tool Usage & Constraints:**
  - **Atomicity:** `run_shell_command` rejects chained commands (e.g., `&&`, `|`, `;`). Execute exactly **one** command per tool call.
  - **Paging:** Always use the `--no-pager` flag for tools like `jj` and `bd` to ensure full output is captured.
  - **Efficiency:** Use `jj commit -m "message"` to save work in a single tool call instead of separate `jj describe` and `jj new` calls.
  - **Discovery:** Use `search_file_content` for code discovery and `read_file` to verify file content before editing.
  - **Verification:** Always verify changes with `uv run basedpyright`.
- **Safety:**
  - Explain any file deletion or shell commands that modify the system state outside the project directory.
- **Commit Protocol:**
  - **Post-Task:** Commit changes after completing a request/task.
  - **Small Tasks:** Ask for user confirmation before committing minor changes.
  - **No Changes:** Do **not** commit if the task involved no changes to tracked files.

## Issue Tracking

This project uses **bd (beads)** for issue tracking.
Run `bd prime` for workflow context, or install hooks (`bd hooks install`) for auto-injection.

**Quick reference:**

- `bd ready` - Find unblocked work
- `bd create "Title" --type task --priority 2` - Create issue
- `bd close <id>` - Complete work
- `bd sync` - Sync with git (run at session end)

For full workflow details: `bd prime`

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY: //**TODO**: Use `jj` instead.//

   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```

5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**

- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
