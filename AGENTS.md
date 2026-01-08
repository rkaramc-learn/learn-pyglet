# AGENTS.md

## Project Overview

`chaser-game` is a Python-based interactive desktop application built using the `pyglet` library. It demonstrates fundamental 2D game development concepts including sprite rendering, continuous movement logic (keyboard and mouse), collision handling (basic window bounds), and audio playback (sound effects and looped background music).

**Recent Features:**

- Sprite sheet animation (mouse sprite).
- Simple AI: Kitten automatically chases the mouse sprite when idle.
- Linear Interpolation (Lerp) for smooth mouse movement.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture and core components.

## Dependencies

- **Runtime:**
  - `pyglet >= 2.1.11`: The core multimedia library.
  - `pyyaml >= 6.0`: YAML parsing for asset manifest.
  - `python >= 3.13`: The execution environment.
- **Development:**
  - `basedpyright >= 1.37.0`: Static type checker (Strict).
  - `ruff >= 0.14.10`: Code formatter and linter (Strict).
  - `pytest >= 8.3.4`: Testing framework (Strict).
- **Package Manager:**
  - `uv`: Used for dependency resolution, environment management, and script execution.
- **External Tools:**
  - `ffmpeg`: Used for media conversion (e.g. creating sprite sheets).
  - `bd` (Beads): Issue tracker/memory tool.

## Environment Setup

See [docs/SETUP.md](docs/SETUP.md) for installation and execution instructions.

## Development Workflow

1. **Version Control:** The project uses `jj` (Jujutsu) backed by Git.

   - **Revset Alias:** If `current-branch` alias is not configured (check with `jj config list | findstr "current-branch"`), configure it:

     ```bash
     jj config set --repo revset-aliases.current-branch "heads(::@ & bookmarks())"
     ```

   - **Save Work:** Use `jj commit -m "message"` as the primary way to save changes. It is more efficient than `jj describe` followed by `jj new` as it performs both in one tool call.
   - **Export to Git:** Use `jj git export` to write jj commits to the underlying Git repository (needed for beads sync).
   - **Untracking Files:** Use `jj file untrack <path>` to stop tracking a file without deleting it.
   - **Listing Files:** Use `jj file list` (add `--no-pager` for full output in non-interactive shells).
   - **Note:** Large binary files (>1MB) are strictly ignored via `.gitignore`.

2. **Running:**
   - `uv run chaser`
3. **Testing/Verification:**
   - **Unit Tests:** `uv run pytest` (MUST pass before completion).
   - **Static Analysis:** `uv run basedpyright` (MUST pass before completion).
   - **Manual:** Run the app to verify visual/audio behavior.

## Coding Standards

- **Type Safety:** All code must be fully type-hinted. `basedpyright` is the authority.
- **Style:** PEP 8 compliance. Enforced by `ruff`.
- **Structure:** Follow the `src` layout pattern.
- **Resources:** Use `pyglet.resource` for loading assets relative to the script directory.
- **Docstrings:** Use Google-style docstrings for all public functions and classes.
- **Naming:**
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

## Operational Guidelines for Agents

- **Asset Management:** Do not blindly create or commit large binary assets. Check file sizes.
  - If creating derived assets (like sprite sheets), verify they are added to `.gitignore`.
- **Environment & Shell Awareness:**
  - **Check OS:** Identify the operating system (`win32`, `linux`, `darwin`) before running commands.
  - **Windows:** The shell is **PowerShell**.
    - Use `Get-ChildItem -Force` instead of `ls -a`.
    - Use `Invoke-WebRequest -Uri <url> -OutFile <path>` instead of `curl` or `wget`.
  - **Linux/macOS:** Use standard `bash`/`sh` commands (e.g., `ls -a`, `curl`).
  - **Efficiency:** Use `jj commit -m "message"` to save work in a single tool call instead of separate `jj describe` and `jj new` calls.
  - **Verification:** Always verify changes with `uv run basedpyright`.
- **Safety:**
  - Explain any file deletion or shell commands that modify the system state outside the project directory.
- **Commit Protocol:**

  - **Post-Task:** Commit changes after completing a request/task.
  - **Agent Discretion:** Decide whether to commit based on:
    - **Significance:** Does the change add value or complete a logical unit of work?
    - **Impact:** Could the change affect other parts of the codebase?
    - **Coherence:** Is the change self-contained and well-described?
    - **Reversibility:** Would it be harder to undo if not committed separately?
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

## Session Workflows

### Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below.

**MANDATORY WORKFLOW (Jujutsu + Beads):**

1. **File issues for remaining work** - Create linked issues for discovered work:

   ```bash
   bd create "Issue title" --description="Details" -p 2 --deps discovered-from:<parent-id> --json
   ```

2. **Run quality gates** (if code changed) - Tests, linters, builds

   ```bash
   uv run basedpyright
   uv run pytest
   uv run ruff check --fix
   uv run ruff format
   ```

3. **Commit work** (if not already done)

   ```bash
   jj commit -m "type(scope): description"
   ```

4. **Export jj changes to Git** (required for external tools like beads)

   ```bash
   jj git export
   ```

5. **Update issue status** - Close completed issues:

   ```bash
   bd close <id> --reason "Done" --json
   ```

6. **Verify** - Confirm all changes are committed

   ```bash
   jj status  # MUST show "The working copy has no changes."
   ```

### Push to remote

**When the user requests to push changes to remote**, you MUST complete ALL steps below.

1. **Fetch from remote**

   ```bash
   jj git fetch
   ```

2. **Merge current change with trailing bookmarks**

   ```bash
   jj new "current-branch" @-
   ```

3. **Resolve merge conflicts** - If `jj status` shows conflicts:

   - View conflicted files to identify conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
   - For simple conflicts (e.g., adjacent line changes): edit files to resolve
   - For complex conflicts (e.g., semantic conflicts, large refactors): notify user with context and request assistance
   - After resolution: `jj resolve --mark` to mark files as resolved

4. **Verify** - Confirm no conflicts remain

   ```bash
   jj status  # MUST NOT show "(conflict)" or "Warning: There are unresolved conflicts..."
   ```

5. **Inspect bookmarks** - View bookmarks that need to be moved forward

   ```bash
   jj log -r "current-branch"
   ```

6. **Update bookmarks** - Move all bookmarks behind current change forward to @-

   ```bash
   jj bookmark move --from "current-branch" --to @-
   ```

7. **Push to remote**

   ```bash
   jj git push
   ```

**CRITICAL RULES:**

- Work is NOT complete until bookmarks are moved and pushed
- Use `jj log -r "current-branch"` to verify which bookmark will be updated
- Use `jj bookmark move --from "current-branch" --to @-` to move trailing bookmark
- Always use `jj git export` before `bd sync` to ensure Git state is current
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

**When to run `bd sync` manually:**

- Before switching contexts or running other git operations (to bypass the debounce delay)
- When using Git worktrees (auto-sync is disabled)
- After `git pull` to ensure local state matches remote
- If auto-sync daemon is disabled

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
