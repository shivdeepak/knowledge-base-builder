# Knowledge Base Builder

An [Agent Skill](https://agentskills.io/specification) (Cursor, Claude Code,
Claude Web, Cowork) that turns any directory of notes, docs, or plans into a
knowledge base an LLM can navigate efficiently — using **progressive
disclosure** instead of embeddings or a vector database.

Packaged with [skillship](https://github.com/shivdeepak/skillship) for
cross-surface distribution.

## Installation

Install via [skillship](https://github.com/shivdeepak/skillship) (requires
Node.js >= 18):

```bash
npx skillship@latest install shivdeepak/knowledge-base-builder -a cursor -a claude-code
```

Or install directly with the `skills` CLI:

```bash
npx skills add shivdeepak/knowledge-base-builder
```

## The idea

Every directory gets a lightweight `index.md`; every note gets a one-line
`summary` in its frontmatter. An agent answers a question by reading the root
index, scanning summaries, and opening only the few files that matter — never
loading the whole corpus or running similarity search.

At personal and team scale (up to tens of thousands of files) this is faster to
set up than a RAG pipeline, fully transparent, version-control friendly, and
needs no database. **The filesystem is the state; Markdown is the wire format.**

The work has two parts, both done by the agent:

- **Summaries** require reading and understanding a file → the judgment-heavy
  part.
- **Indexes** are mechanical assembly of those summaries into an `index.md` per
  directory → repetitive but still the agent's job. No scripts, no database.

## What your knowledge base looks like

After running the skill, a folder of notes becomes a self-navigating tree — an
`index.md` in every directory, a one-line `summary` in every note's frontmatter:

```text
my-knowledge-base/
├── index.md                  ← root: navigation protocol + generated map of everything
├── projects/
│   ├── index.md              ← area index: lists each note with its summary
│   ├── website-rewrite.md      ┐  ---
│   └── q3-roadmap.md           │  title: Q3 roadmap
│                               │  summary: The three shipping milestones, owners, and risks.
│                               │  ---  ← frontmatter is what the index reads
└── thoughts/
    ├── index.md
    └── on-focus.md

An agent answers a question by walking top-down:
  index.md  →  scan area summaries  →  open the 1–3 areas that fit
            →  scan note summaries  →  open only the few notes that match
```

## Repository layout

| Path | What it is |
| --- | --- |
| `knowledge-base-builder/SKILL.md` | The skill entrypoint: when it applies and the 6-step workflow an agent follows. |
| `knowledge-base-builder/references/conventions.md` | Exact schemas — note frontmatter, `index.md` anatomy, summary-writing rules, naming, root navigation protocol, and how to build the index region by hand. |
| `release-please-config.json`, `.release-please-manifest.json`, `version.txt` | Release automation via release-please + Conventional Commits. |
| `.github/workflows/validate.yml` | Validates the skill on every PR/push via `npx skillship validate`. |
| `.github/workflows/release.yml` | Cuts releases and uploads `knowledge-base-builder.skill` to GitHub Releases. |
| `snippets/cursor-rule.mdc` | Cursor rule snippet pointing agents at the skill. |
| `snippets/claude-md.md` | Claude AGENTS.md snippet for Claude Code consumers. |

## How to use it

The entrypoint is `knowledge-base-builder/SKILL.md`; read it first, then
`knowledge-base-builder/references/conventions.md`
for the exact schemas. A Cursor agent loads these automatically, but the steps
are the same whether you drive them yourself or let the agent run them. Building
a knowledge base goes through six steps:

1. **Assess** the directory before changing anything, and report what's there
   before any large-scale edits.
2. **Decide the structure** — keep sensible existing folders, get consent before
   moving files, and never delete content.
3. **Summarize every note** — write an honest one-line `summary` into each
   note's frontmatter. This is the load-bearing step, and the one that needs
   real understanding of each file.
4. **Build the indexes** — in each directory, write an `index.md` that lists its
   sub-areas and notes with their summaries, following the conventions.
5. **Make the base self-describing** — write the navigation protocol into the
   root `index.md` so a fresh reader (or cold agent) knows how to traverse it.
6. **Maintain it** — when notes change, refresh their summaries and update the
   affected `index.md` files; the navigation protocol in the root index tells
   any future agent how to do this.

Each `index.md` is a plain, human-readable page — a short intro plus a listing
of the area's sub-areas and notes with their summaries. There are no special
markers or generated blocks; the agent writes and updates the whole file by
hand, like a good README. Building an index never writes summaries, moves files,
or deletes anything; those need judgment and stay deliberate, separate steps.

## When this fits (and when it doesn't)

Use it for collections a person or team curates: notes, plans, journals,
research, project docs, decision logs — content read by an LLM that can reason
about which files to open.

It is **not** for very large, high-churn corpora (millions of chunks, constant
ingestion, fuzzy semantic recall across everything at once). Those want vector
search or GraphRAG.
