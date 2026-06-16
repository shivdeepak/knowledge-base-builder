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

# projects

...intro and listing...
```

## index.md anatomy

An `index.md` is just a readable Markdown page for one directory — a short intro
and a list of what's inside, grouped so a person (or agent) can scan it. There
are no special markers or generated blocks; you write and update the whole file
by hand, the same way you'd keep a good README current.

```markdown
---
summary: Active and archived project plans, one file per project.
---

# projects

Plans and decision logs, one file per project. Start with the roadmap.

## Areas
- [`archive/`](archive/index.md) — Completed projects kept for reference.

## Notes
- [Q3 roadmap](q3-roadmap.md) _(active)_ — The three shipping milestones, owners, and risks.
- [On focus](on-focus.md) — Why I lose focus mid-week and what I'm trying.

## Files
- [`diagram.png`](diagram.png)
```

What goes in each group:

- **Areas** — one bullet per sub-directory, linking to its `index.md`, with the
  `summary` from that sub-directory's index.md frontmatter as the one-liner.
- **Notes** — one bullet per `.md`/`.markdown` file (excluding `index.md`),
  linking to the file, showing its `title` (or filename stem), an optional
  `_(status)_` badge, and its `summary`.
- **Files** — one bullet per non-note file (PDFs, images, etc.).

Keep the listing in sync with the directory: when a note's summary or a
sub-area's summary changes, update the matching line. Drop a group heading
entirely if it has no entries, and skip dotfiles and infrastructure dirs
(`.git`, `.obsidian`, `node_modules`, `__pycache__`). Every directory gets an
`index.md`, including empty ones (which can simply say the area is empty for
now).

## Root navigation protocol

The root `index.md` opens with a short protocol, before the listing, that tells
any future agent (or person) how to use the knowledge base. This makes the base
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
then update the affected directory's index.md (and any parent whose area summary
changed) to match.

## Areas
...listing...
```

## Naming

- Files: lowercase, hyphenated, descriptive (`website-rewrite-decisions.md`). Date-
  prefix journal-style notes (`2026-06-14-standup.md`) so they sort chronologically.
- Directories: short topic names (`projects`, `thoughts`, `reference`, `people`).
- Keep the tree shallow. Two or three levels handles thousands of notes; deeper nesting
  hurts navigability more than it helps.

## What index-building does and doesn't touch

- **Does:** keep each directory's `index.md` listing in sync with its contents
  and the notes' frontmatter summaries.
- **Doesn't:** write summaries, move or rename files, or delete anything. Those
  need judgment (and the user's consent), so handle them as deliberate, separate
  steps rather than folding them into an index update.
