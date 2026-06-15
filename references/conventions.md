# Knowledge base conventions

Exact formats for the structure the skill produces. SKILL.md points here so the main
instructions stay short. Read this when you need the precise schema for frontmatter,
index files, or the navigation protocol.

## Why these conventions exist

The whole system rests on one trick: an agent should be able to find the right content
without reading everything. It reads a lightweight index, scans one-line summaries,
and opens only the few files that matter. For that to work, two things must be true
everywhere: every note carries an honest one-line `summary`, and every directory has an
`index.md` that surfaces those summaries. Get those two right and the knowledge base
stays navigable as it grows, with no embeddings and no database.

## Note frontmatter

Every note (`.md` / `.markdown`) starts with YAML frontmatter:

```markdown
---
title: On focus
created: 2026-06-14
status: active
tags: [productivity, planning]
summary: Why I lose focus mid-week and the three experiments I'm trying to fix it.
---

# On focus

...body...
```

Field guide:

- `title` — human-facing name. If omitted, the filename stem is used. Set it when the
  filename is terse or dated (e.g. `2026-06-14.md`).
- `summary` — **the load-bearing field.** One sentence describing what is *in* the file
  and when someone would want it. Not a teaser. See "Writing summaries" below.
- `status` — optional lifecycle tag: `active`, `draft`, `archived`, `idea`, `done`.
  Shown as a badge in the index so stale notes are visible at a glance.
- `tags` — optional list for cross-cutting themes. Inline (`[a, b]`) or block list both
  parse.
- `created` / `updated` — optional dates; useful but not used by the index builder.

Only `summary` (and ideally `title`) is required for the index to be useful. Other
fields are conveniences.

## Writing summaries

A summary is good when a reader who sees only the index can decide whether to open the
file. Describe contents and use, concretely.

- Weak: `Notes about work.`
- Weak: `Some thoughts on the Q3 plan.` (teaser — what thoughts?)
- Strong: `Q3 roadmap: the three shipping milestones, owners, and the deadline risks.`
- Strong: `Decision log for the website rewrite — why we chose Astro over Next.`

Keep it to one sentence. Lead with the noun (what it is), then the payoff (why you'd
open it).

## Directory summaries

A directory describes itself through the `summary` in the frontmatter of its own
`index.md`. The parent directory's index reads that and uses it as the area's one-liner.

```markdown
---
summary: Active and archived project plans, one file per project.
---

# projects — index

<!-- BEGIN AUTO-INDEX ... -->
...
<!-- END AUTO-INDEX -->
```

## index.md anatomy

Each `index.md` has two parts:

1. **A human region** — anything you write outside the auto-index markers is preserved
   across rebuilds: a title, an intro paragraph, the navigation protocol (root only),
   hand-picked "start here" links.
2. **An auto-generated region** — everything between the markers is owned by
   `build_index.py` and rewritten on every run:

```markdown
<!-- BEGIN AUTO-INDEX (managed by build_index.py — edits inside are overwritten) -->

### Areas
- [`projects/`](projects/index.md) — Active and archived project plans.

### Notes
- [On focus](on-focus.md) _(active)_ — Why I lose focus mid-week and what I'm trying.

### Files
- [`diagram.png`](diagram.png)

<!-- END AUTO-INDEX -->
```

Never hand-edit inside the markers — your changes will be overwritten next rebuild.
Put durable content above or below them.

## Root navigation protocol

The root `index.md` should carry a short protocol, above the auto-index block, that
tells any future agent (or person) how to use the knowledge base. This makes the base
self-describing: drop a fresh session in front of it and it knows how to navigate.
Use this template:

```markdown
# <name> — knowledge base

How to use this knowledge base (progressive disclosure):
1. Read this index. Skim the area summaries below and pick the 1-3 areas that fit the question.
2. Open those areas' `index.md` files and scan the note summaries.
3. Open only the handful of notes whose summaries match. Don't read everything.
4. If nothing fits, say so rather than guessing — the base may not cover it yet.

When you add or change notes, write/refresh the `summary` in each note's frontmatter,
then run `python scripts/build_index.py` to rebuild every index.

<!-- BEGIN AUTO-INDEX ... -->
...
<!-- END AUTO-INDEX -->
```

## Naming

- Files: lowercase, hyphenated, descriptive (`website-rewrite-decisions.md`). Date-
  prefix journal-style notes (`2026-06-14-standup.md`) so they sort chronologically.
- Directories: short topic names (`projects`, `thoughts`, `reference`, `people`).
- Keep the tree shallow. Two or three levels handles thousands of notes; deeper nesting
  hurts navigability more than it helps.

## What the script does and doesn't do

- **Does:** assemble `index.md` in every directory from existing frontmatter; preserve
  human regions; flag notes missing a summary (`--report`); check for staleness
  (`--check`, useful in a git pre-commit hook or CI).
- **Doesn't:** write summaries, move or rename files, delete anything. Those need
  judgment (and the user's consent), so they stay with the LLM.
