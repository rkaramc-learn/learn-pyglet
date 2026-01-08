---
name: analyzing-refactoring-tasks
description: Analyzes refactoring tasks in beads by extracting current code, refactored code, pros/cons, and dependencies. Use when asked to explain a refactoring bead or update its description with detailed analysis.
---

# Analyzing Refactoring Tasks Skill

Performs deep analysis of refactoring-type issues in a bead management system. Produces a comprehensive description with code snippets, trade-offs, and integration status.

## Capabilities

- **Extract current code**: Finds and isolates the before state from relevant files
- **Extract refactored code**: Locates the after state in new/modified files
- **Identify pros/cons**: Documents benefits and drawbacks of the refactoring
- **Detect dependencies**: Finds related issues and integration blockers
- **Append analysis to notes**: Adds formatted analysis to bead notes field, preserving history and showing progression

## Workflow

### 1. Load Issue Details

Get the full bead description to understand what's being refactored.

```bash
bd show <bead-id> --json
```

### 2. Identify Scope Files

Parse the bead description to find:
- Which files contain "current" (pre-refactoring) code
- Which files contain "refactored" (post-refactoring) code
- Key classes, functions, or modules involved

Look for keywords like:
- "before" / "after"
- "old" / "new"
- "monolithic" / "encapsulated"
- File paths mentioned in description

### 3. Extract Code Snippets

Read files identified in scope and extract:

**Current state**: Look for:
- Duplicated logic scattered across files
- Mixed concerns in single functions
- Hardcoded values or magic numbers
- Verbose/repetitive patterns

**Refactored state**: Look for:
- Extracted classes/functions
- Dedicated modules
- Reusable abstractions
- Clear separation of concerns

**Extract 5-10 lines per snippet** showing the key transformation.

### 4. Analyze Dependencies

Run bd queries to find:
- Parent issues (what this depends on)
- Child issues (what depends on this)
- Related issues mentioning same modules

```bash
bd list --json | jq '.[] | select(.title | contains("refactor") or .title | contains("Mouse") or .title | contains("Kitten"))'
```

### 5. Document Pros/Cons

List 3-5 of each:

**Pros**: Benefits of the refactoring
- Testability improvements
- Code reuse opportunities
- Type safety enhancements
- Decoupling benefits

**Cons**: Trade-offs and limitations
- Remaining tight coupling
- New abstractions needed
- Performance impact (if any)
- Integration challenges

### 6. Integration Status

Assess current state:
- Is the refactoring complete?
- Are old code patterns still used in the codebase?
- What's the integration plan?
- What are the next steps?

### 7. Append Analysis to Notes

Read current notes, then append new analysis with timestamp and version marker:

```bash
# Get existing notes
bd show <bead-id> --json | jq -r '.[0].notes // ""'

# Build new note entry with timestamp
NEW_NOTE="## Analysis - $(date +'%Y-%m-%d %H:%M')

**Status:** [Complete/In Progress/Planned]

**Current Code Structure (Before):**
\`\`\`[language]
[snippet showing old approach]
\`\`\`

**Refactored Code (After):**
\`\`\`[language]
[snippet showing new approach]
\`\`\`

**Pros:**
- [benefit 1]
- [benefit 2]
- [benefit 3]

**Cons:**
- [trade-off 1]
- [trade-off 2]
- [trade-off 3]

**Integration Status:**
- [What's implemented]
- [What's pending]
- [Next steps]

**Dependencies/Related:**
- [Related issues with context]"

# Append to existing notes
bd update <bead-id> --notes="$EXISTING_NOTES

---

$NEW_NOTE"
```

Each analysis iteration appears as a timestamped entry in notes, showing progression and decisions over time. The description remains unchanged with original task definition.

## Example Workflow

**Input**: `pyglet-v6q` (refactor mouse/kitten into entities)

**Step 1**: `bd show pyglet-v6q --json` → Get task description

**Step 2**: Identify scope → `game_running.py` (current), `entities/mouse.py` and `entities/kitten.py` (refactored)

**Step 3**: Extract snippets from both files

**Step 4**: Search for related issues → Find `pyglet-v5q.3` (parent), `pyglet-jb4`, `pyglet-eb0` (related features)

**Step 5**: Analyze:
- **Pros**: Encapsulation, testability, reusability, type safety
- **Cons**: Sprite dimensions separate, rendering still coupled, duplicate state

**Step 6**: Assessment → Complete, but GameRunningScreen integration pending

**Step 7**: Append analysis to notes field:
```bash
EXISTING=$(bd show pyglet-v6q --json | jq -r '.[0].notes // ""')
NEW_NOTE="## Analysis - 2026-01-08 12:30

**Status:** Complete

**Current Code Structure (Before):**
\`\`\`python
# In GameRunningScreen
self.kitten_center_x = window.width * CONFIG.KITTEN_START_X_RATIO
self.mouse_health = MAX_HEALTH
self.kitten_center_x += (dx / distance) * travel
\`\`\`

[...rest of analysis...]"

bd update pyglet-v6q --notes="$EXISTING

---

$NEW_NOTE"
```

Notes now shows full analysis history with timestamps.

## Tips

- **Focus on transformation**: Show the most revealing before/after snippets, not all code
- **Use clear headers**: Make sections skimmable with bold headings and bullet points
- **Link related work**: Reference other beads by ID when dependencies exist
- **Be concise**: Keep prose minimal, let code and structure speak
- **Check integration**: Always assess whether old patterns are still in use elsewhere
- **Find follow-ups**: Use the cons list to suggest next refactoring steps
- **Preserve history**: Each analysis appended to notes with timestamp shows progression
- **Track decisions**: Document what changed between analyses and why
- **Show evolution**: Later analyses can reference earlier findings and note improvements

## Tools Used

- `bd list/show` - Query issue tracker
- `Grep` / `Read` - Extract code from files
- `bd update` - Write analysis back to bead

