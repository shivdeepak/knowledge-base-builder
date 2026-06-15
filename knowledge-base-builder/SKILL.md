---
name: knowledge-base-builder
description: >-
  Turn a folder of notes, docs, or plans into an LLM-navigable knowledge base:
  index.md files and per-note summaries, no vector DB. Trigger: organize notes,
  second brain, knowledge base.
license: MIT
metadata:
  version: "1.1.0" # x-release-please-version
---

# Knowledge Base Builder

Turn a directory into a knowledge base that an LLM can navigate efficiently,
using
**progressive disclosure**: lightweight index files at every level, and a
one-line
summary on every note. An agent answers a question by reading the root index,
scanning
summaries, and opening only the few files that matter — instead of loading the
whole
corpus or running similarity search over embeddings. At personal and team scale
(up to
tens of thousands of files) this is faster to set up, fully transparent,
version-control
friendly, and needs no database. The filesystem is the state; Markdown is the
wire
format.

The work splits cleanly. Writing each note's **summary** requires reading and
understanding the file — that is your job as the model. Assembling those
summaries into
**index.md** files is mechanical and repetitive — that is the bundled script's
job. Keep
that division: you supply meaning, the script supplies structure.

Read `references/conventions.md` for the exact frontmatter schema, index.md
format,
naming rules, and the root navigation protocol. The workflow below tells you
when.

## When this fits (and when it doesn't)

Use it for collections a person or team curates: notes, plans, journals,
research,
project docs, decision logs. It shines when content is read by an LLM that can
reason
about which files to open.

It is not the right tool for very large or high-churn corpora (millions of
chunks,
constant ingestion, fuzzy semantic recall across everything at once) — those
want vector
search or GraphRAG. If the user clearly needs that scale, say so plainly rather
than
forcing this pattern.

## Workflow

### 1. Assess the directory

Before changing anything, look. List the tree (e.g. `find <dir> -type f`).
Sample a
handful of files to learn the content and whether they
already have frontmatter. Note what exists: Is there structure or is it a flat
dump? Do
notes have summaries? Are there already index.md files (this may be a refresh,
not a
first build)? Are there non-markdown files (PDFs, images) to account for?

Tell the user what you found and what you propose before doing large-scale
edits.

### 2. Decide on structure (and get consent before moving anything)

If the directory is already organized into sensible folders, keep it — work
additively.
If it is a flat pile, propose a small set of top-level areas (e.g. `projects/`,
`thoughts/`, `reference/`) grouped by how the user thinks about their material,
and ask
before reorganizing. Keep the tree shallow; two or three levels handle thousands
of
notes.

Operate non-destructively. Never delete user content. Prefer moving over
rewriting, and
if the directory isn't under version control, suggest `git init` first so every
change is
reversible. Restructuring is the one step that can lose work — treat the user's
consent
as the gate.

### 3. Summarize every note (this is the core task)

For each note, ensure its frontmatter has at least a `title` and a `summary`,
adding
`status` and `tags` where useful. Where a note already has a good summary, leave
it.
Where it's missing or weak, read the file and write one.

A summary earns its place when a reader who sees only the index can decide
whether to
open the file. Lead with what the file *is*, then why someone would open it —
concrete,
one sentence, not a teaser. (`references/conventions.md` has good/weak
examples.) These
summaries are the entire reason progressive disclosure works, so spend real
attention
here rather than generating filler.

For directories, write a `summary` into the frontmatter of that directory's
index.md so
the parent index can describe the area in one line.

### 4. Build the indexes

Copy the bundled script into the knowledge base itself —
`<knowledge-base-root>/scripts/build_index.py` — so the base is self-contained:
the maintenance loop, the navigation protocol, and any pre-commit hook all
resolve to a script that lives alongside the notes, even for a session that has
never seen this skill. Then run it to assemble every index.md from the
frontmatter you just wrote:

```bash
python scripts/build_index.py <knowledge-base-root>
```

It walks the tree and, in each directory, writes an index.md listing sub-areas
and notes
with their summaries. It only owns the region between the AUTO-INDEX markers —
anything
you write outside them is preserved. Use `--report` to list notes still missing
a
summary so you can circle back, and `--check` (writes nothing, exits non-zero on
stale
indexes) for a git pre-commit hook or CI.

### 5. Make the base self-describing

Write the navigation protocol into the root index.md, above the auto-index block
(see
the template in `references/conventions.md`). This tells any future session how
to
traverse the base — read index, scan summaries, open the few relevant files — so
the
knowledge base works for a cold agent that has never seen it, not just for this
conversation.

### 6. Hand off maintenance

Leave the user with the simple upkeep loop: when you add or edit notes, refresh
the
`summary` in the frontmatter, then re-run `build_index.py` to rebuild the
indexes.
Offer to wire the `--check` mode into a git pre-commit hook so indexes never
drift out of
sync with the notes.

## Output

A directory where every folder has an index.md, every note has a frontmatter
summary, the
root carries a navigation protocol, and a copy of `scripts/build_index.py` lives
in the
base (at `<root>/scripts/build_index.py`) to keep it all in sync. The result is
browsable
by a person and navigable by any LLM, with the structure visible and editable as
plain
text.
