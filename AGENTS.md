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

1. **Version Control:** The project uses `jj` (Jujutsu) backed by Git.
   - **Save Work:** Use `jj commit -m "message"` as the primary way to save changes. It is more efficient than `jj describe` followed by `jj new` as it performs both in one tool call.
   - **Export to Git:** Use `jj git export` to write jj commits to the underlying Git repository (needed for beads sync).
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
  - **Ignore Bead Files:** Do not mention `.beads/issues.jsonl` in commit messages—it is auto-managed by `bd`.
  - **Message Format:** Use [Conventional Commits](https://www.conventionalcommits.org/):

    - `type(scope): short description` (50 chars max for subject)
    - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
    - Add blank line + bullet points for detailed changes
    - Example:

      ```text
      feat(entities): add Character base class

      - Add Entity dataclass with position, velocity, state
      - Implement clamp_to_bounds for window collision
      ```

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

**When ending a work session**, you MUST complete ALL steps below.

**MANDATORY WORKFLOW (Jujutsu + Beads):**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
   ```bash
   bd create "Title" --type task --priority 2
   ```

2. **Run quality gates** (if code changed) - Tests, linters, builds
   ```bash
   uv run basedpyright
   uv run pytest
   uv run ruff lint --fix
   uv run ruff format --fix
   ```

3. **Commit work** (if not already done)
   ```bash
   jj commit -m "type(scope): description"
   ```

4. **Export jj changes to Git** (required for external tools like beads)
   ```bash
   jj git export
   ```

5. **Update issue status** - Close finished work
   ```bash
   bd close <issue-id>
   ```

6. **Sync beads to remote**
   ```bash
   bd sync
   ```

7. **Verify** - Confirm all changes are pushed
   ```bash
   jj status  # MUST show "The working copy has no changes."
   ```

## Push the changes to remote

**When the user requests to push changes to remote**, you MUST complete ALL steps below.

1. **Fetch from remote**
   ```bash
   jj git fetch
   ```

2. **Update bookmark**
   ```bash
   jj new main @-    # Merge current change with main
   ```

3. **Resolve merge conflicts** - If there are any merge conflicts, request user to resolve and commit

4. **Continue with Push to Remote**
   ```bash
   jj status  # MUST NOT show "(conflict)" or "Warning: There are unresolved conflicts..."
   ```
   If conflicts remain, alert user and stop.

5. **Update bookmark** - Move `main` to current change
   ```bash
   jj bookmark move main --to @-
   ```

6. **Push to remote**
   ```bash
   jj git push
   ```


**CRITICAL RULES:**

- Work is NOT complete until `jj bookmark set main -r @-` succeeds
- Always use `jj git export` before `bd sync` to ensure Git state is current
- Always update bookmark with `jj bookmark set main -r @-` (the committed work) before pushing
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds


<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs with git:

- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

<!-- END BEADS INTEGRATION -->
