# Bug Report: `bd dep` nil pointer dereference

## Summary

The `bd dep <issue-id> --blocks <blocked-id>` shorthand syntax causes a nil pointer dereference panic.

## Environment

- **bd version**: 0.44.0 (d7221f68)
- **OS**: Windows 11
- **Shell**: PowerShell 7

## Minimum Reproducible Example

```bash
# 1. Create two test issues
bd create --title "Test Issue A" --priority 3 --type task
# Created: pyglet-xxx

bd create --title "Test Issue B" --priority 3 --type task
# Created: pyglet-yyy

# 2. Try to add a blocking dependency using shorthand syntax
bd dep pyglet-xxx --blocks pyglet-yyy
# PANIC: nil pointer dereference
```

## Expected Behavior

The command should create a blocking dependency where `pyglet-xxx` blocks `pyglet-yyy`.

## Actual Behavior

```
panic: runtime error: invalid memory address or nil pointer dereference
[signal 0xc0000005 code=0x0 addr=0x78 pc=0xe294bb]

goroutine 1 [running]:
main.warnIfCyclesExist({0x0?, 0x0?})
        /home/runner/work/beads/beads/cmd/bd/dep.go:48 +0x3b
main.init.func40(0x1da33e0, {0xc00042e270, 0x1, 0x3?})
        /home/runner/work/beads/beads/cmd/bd/dep.go:182 +0x91f
github.com/spf13/cobra.(*Command).execute(0x1da33e0, {0xc00042e210, 0x3, 0x3})
        /home/runner/go/pkg/mod/github.com/spf13/cobra@v1.10.2/command.go:1019 +0xa91
github.com/spf13/cobra.(*Command).ExecuteC(0x1db5640)
        /home/runner/go/pkg/mod/github.com/spf13/cobra@v1.10.2/command.go:1148 +0x46f
github.com/spf13/cobra.(*Command).Execute(...)
        /home/runner/go/pkg/mod/github.com/spf13/cobra@v1.10.2/command.go:1071
main.main()
        /home/runner/work/beads/beads/cmd/bd/main.go:861 +0x1a
```

## Analysis

The crash occurs in `warnIfCyclesExist()` at `dep.go:48`, suggesting:

1. The function receives a nil pointer when checking for dependency cycles
2. The cycle check is called before validating the dependency was created successfully
3. Missing nil check on the return value from dependency creation

## Workaround

Use the explicit `bd dep add` syntax instead:

```bash
# This works:
bd dep add pyglet-yyy pyglet-xxx
# Meaning: pyglet-yyy depends on pyglet-xxx (pyglet-xxx blocks pyglet-yyy)
```

## Related

- `bd dep --help` shows the shorthand syntax as valid
- The `bd dep add` subcommand works correctly

## Date Reported

2026-01-15
