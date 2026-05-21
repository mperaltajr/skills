# Slide Lab agents

These are the **subagent definitions** Slide Lab uses to do parallel work — one agent per slide, one orchestrator per deck.

Claude Code looks for agent files in `~/.claude/agents/`, NOT inside a skill folder. So after cloning this repo to `~/.claude/skills/`, you need to copy the four `.md` files in this folder into your `~/.claude/agents/` folder.

## What's in here

| File | What it is |
|---|---|
| `deck-builder.md` | Deck-level orchestrator. Runs prep → fanout-instructions → finalize → review across a whole brief. |
| `slide-designer.md` | Produces design options from a brief. Two modes: deck-level (2 options × N slides) or per-slide (4 options for one slide). |
| `slide-builder.md` | Per-slide orchestrator. Plans the parallel build of 4 option slides from a design spec and packages them. |
| `slide-builder-worker.md` | The leaf worker. Builds exactly ONE option slide. Dispatched four-at-a-time by `slide-builder`. |

## Install

### One-time copy (Windows PowerShell)

```powershell
Copy-Item -Path "$HOME\.claude\skills\agents\*.md" -Destination "$HOME\.claude\agents\" -Force
```

### One-time copy (macOS / Linux)

```bash
mkdir -p ~/.claude/agents
cp ~/.claude/skills/agents/*.md ~/.claude/agents/
```

### Verify

After copying, ask Claude Code: *"list my agents — do you see deck-builder, slide-designer, slide-builder, and slide-builder-worker?"* If all four come back, you're set.

## Re-syncing after a `git pull`

The skills repo is the source of truth. When you pull updates, the files in `~/.claude/skills/agents/` change but your `~/.claude/agents/` copies don't — so re-run the copy command above after every `git pull` that touches this folder.

If you'd rather not think about it, you can replace the copies with symlinks (one-time setup, auto-syncs on pull):

**PowerShell (requires admin or Developer Mode):**
```powershell
Remove-Item "$HOME\.claude\agents\deck-builder.md","$HOME\.claude\agents\slide-designer.md","$HOME\.claude\agents\slide-builder.md","$HOME\.claude\agents\slide-builder-worker.md" -ErrorAction SilentlyContinue
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\agents\deck-builder.md"       -Target "$HOME\.claude\skills\agents\deck-builder.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\agents\slide-designer.md"     -Target "$HOME\.claude\skills\agents\slide-designer.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\agents\slide-builder.md"      -Target "$HOME\.claude\skills\agents\slide-builder.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\agents\slide-builder-worker.md" -Target "$HOME\.claude\skills\agents\slide-builder-worker.md"
```

**macOS / Linux:**
```bash
ln -sf ~/.claude/skills/agents/deck-builder.md         ~/.claude/agents/deck-builder.md
ln -sf ~/.claude/skills/agents/slide-designer.md       ~/.claude/agents/slide-designer.md
ln -sf ~/.claude/skills/agents/slide-builder.md        ~/.claude/agents/slide-builder.md
ln -sf ~/.claude/skills/agents/slide-builder-worker.md ~/.claude/agents/slide-builder-worker.md
```

## Why these aren't bundled inside `slide-builder/`

Claude Code reads skills from `~/.claude/skills/` and agents from `~/.claude/agents/` — they're separate namespaces with separate file conventions. Putting an agent inside a skill folder won't register it. So Slide Lab ships the agent files in this dedicated `agents/` folder, and the install step copies them to the directory Claude Code actually reads.
