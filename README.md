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
npx skillship install knowledge-base-builder -a cursor,claude-code
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

The work splits cleanly:

- **Summaries** require reading and understanding a file → the agent's job.
- **Indexes** are mechanical assembly of those summaries → the script's job
  (`scripts/build_index.py`).

## What your knowledge base looks like

After running the skill, a folder of notes becomes a self-navigating tree — an
`index.md` in every directory, a one-line `summary` in every note's frontmatter:

```text
my-knowledge-base/
├── index.md                  ← root: navigation protocol + auto-generated map of everything
├── scripts/
│   └── build_index.py        ← copied in, so the base maintains itself
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
| `knowledge-base-builder/references/conventions.md` | Exact schemas — note frontmatter, `index.md` anatomy, summary-writing rules, naming, root navigation protocol. |
| `knowledge-base-builder/scripts/build_index.py` | Generates/refreshes every `index.md` from frontmatter. Stdlib-only (PyYAML optional). |
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
4. **Build the indexes** — copy `build_index.py` into the knowledge base so it
   stays self-contained, then run it to assemble every `index.md` from those
   summaries.
5. **Make the base self-describing** — write the navigation protocol into the
   root `index.md` so a fresh reader (or cold agent) knows how to traverse it.
6. **Maintain it** — when notes change, refresh their summaries and re-run the
   script; optionally wire `--check` into a git pre-commit hook so indexes never
   drift.

Running the script directly:

```bash
python knowledge-base-builder/scripts/build_index.py <knowledge-base-root>          # rebuild every index.md
python knowledge-base-builder/scripts/build_index.py <root> --report                # list notes missing a summary
python knowledge-base-builder/scripts/build_index.py <root> --check                 # exit 1 if any index is stale (CI / pre-commit)
```

It only owns the region between the `AUTO-INDEX` markers in each `index.md`.
Anything outside those markers — intros, the navigation protocol, hand-picked
links — is preserved across rebuilds. It never writes summaries, moves files, or
deletes anything; those need judgment and stay with the human or agent.

Requirements & resilience:

- **Python 3.8+.** Older interpreters exit with a clear version message rather
  than a cryptic syntax error.
- **PyYAML is optional.** Install it (`pip install pyyaml`) if your frontmatter
  uses multi-line/folded YAML (e.g. `summary: >-`); otherwise the built-in
  minimal parser handles flat keys and prints a one-line warning so you know the
  fallback is active.
- **Fault-tolerant.** An unreadable note is flagged inline in its index
  (`_(unreadable: ...)_`) instead of aborting the run; per-file/per-directory
  I/O errors are collected, reported on stderr, and surfaced via exit code `2`.

Exit codes: `0` success · `1` stale indexes (`--check` only) · `2` bad root path
or I/O errors.

## When this fits (and when it doesn't)

Use it for collections a person or team curates: notes, plans, journals,
research, project docs, decision logs — content read by an LLM that can reason
about which files to open.

It is **not** for very large, high-churn corpora (millions of chunks, constant
ingestion, fuzzy semantic recall across everything at once). Those want vector
search or GraphRAG.
