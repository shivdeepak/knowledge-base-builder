---
name: knowledge-base-builder
description: >-
  Turn a folder of notes, docs, or plans into an LLM-navigable knowledge base:
  index.md files and per-note summaries, no vector DB. Trigger: organize notes,
  second brain, knowledge base.
license: MIT
metadata:
  version: "1.1.1" # x-release-please-version
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

The work has two parts. Writing each note's **summary** requires reading and
understanding the file — that is the judgment-heavy part. Assembling those
summaries into **index.md** files is mechanical and repetitive, but you do it
too: walk the tree and, in each directory, write an index listing its sub-areas
and notes with their summaries. You supply the meaning, and you keep the
structure in sync. No scripts, no database — just you and Markdown.

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

Now assemble the summaries into index.md files. In each directory, write a
plain, readable index.md that introduces the area in a line or two and lists its
sub-areas and notes, each with its one-line summary — see the example in
`references/conventions.md`. Work bottom-up: a directory describes itself through
the `summary` in its own index.md frontmatter, and its parent's index reads that,
so write a child's index before the parent that links to it.

Write these as documents a person would happily read, not machine output — no
generated-region markers or fenced-off blocks. As you go, keep a list of notes
still missing a `summary` and circle back to write them; an index entry with no
summary is dead weight.

### 5. Make the base self-describing

Open the root index.md with a short navigation protocol (see the template in
`references/conventions.md`). This tells any future session how to traverse the
base — read index, scan summaries, open the few relevant files — so the
knowledge base works for a cold agent that has never seen it, not just for this
conversation.

### 6. Hand off maintenance

Leave the user with the simple upkeep loop: when you add or edit notes, refresh
the `summary` in the frontmatter, then update the index.md in that note's
directory (and any parent whose area summary changed). Because the base is plain
Markdown with a navigation protocol baked into the root index, any future agent —
even one that has never seen this skill — can refresh stale indexes on demand by
following the same conventions.

## Output

A directory where every folder has an index.md, every note has a frontmatter
summary, and the root carries a navigation protocol that teaches any future
session how to traverse and maintain the base. The result is browsable by a
person and navigable by any LLM, with the structure visible and editable as
plain text — no scripts or database to keep in sync.
