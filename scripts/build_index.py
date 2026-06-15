#!/usr/bin/env python3
"""
build_index.py — Regenerate index.md files for a progressive-disclosure knowledge base.

This script does the *mechanical* half of maintaining the knowledge base: it walks a
directory tree and, in every directory, writes (or refreshes) an index.md that lists the
sub-directories and notes it contains, each with the one-line summary taken from that
note's YAML frontmatter. It does NOT write summaries — that is the LLM's job, because a
good summary requires reading and understanding the file. Keep that division of labor:
the model supplies meaning, this script supplies structure.

Only the region between the AUTO-INDEX markers is owned by this script. Anything you
write above or below those markers in an index.md (an intro paragraph, a navigation
protocol, hand-curated links) is preserved across runs.

Usage:
    python build_index.py [ROOT]              # regenerate all index.md under ROOT (default: .)
    python build_index.py [ROOT] --check      # exit 1 if any index is stale; write nothing
    python build_index.py [ROOT] --report     # also print which files are missing summaries

A directory's own summary (used by its parent's index) is read from the `summary` field
in the frontmatter of that directory's index.md. So to describe an "area", write a
summary in the frontmatter of that area's index.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import quote

BEGIN = "<!-- BEGIN AUTO-INDEX (managed by build_index.py — edits inside are overwritten) -->"
END = "<!-- END AUTO-INDEX -->"

# Directories never descended into or indexed.
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".trash", ".vscode"}
# File extensions parsed for frontmatter and treated as "notes".
NOTE_EXTS = {".md", ".markdown"}
# Files that are not listed as notes (infrastructure).
SKIP_FILES = {"index.md", ".DS_Store"}


def try_yaml():
    try:
        import yaml  # type: ignore
        return yaml
    except Exception:
        return None


def parse_frontmatter(text: str) -> dict:
    """Return the YAML frontmatter as a dict, or {} if none.

    Uses PyYAML when available; otherwise falls back to a minimal parser that handles the
    flat keys this knowledge base relies on (title, summary, status, tags). The fallback
    only understands single-line scalars and simple lists — not folded/multi-line YAML
    (e.g. `summary: >-`), so install PyYAML if your notes use those.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")

    yaml = try_yaml()
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
            return data if isinstance(data, dict) else {}
        except Exception:
            pass  # fall through to minimal parser

    data: dict = {}
    current_list_key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if current_list_key and line.lstrip().startswith("- "):
            data.setdefault(current_list_key, []).append(line.lstrip()[2:].strip())
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            current_list_key = key  # a block list follows
        elif value.startswith("[") and value.endswith("]"):
            data[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            data[key] = _unquote(value.strip())
    return data


def _unquote(value: str) -> str:
    """Strip a single matched pair of surrounding quotes, leaving lone quotes intact."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def first_heading_or_line(text: str) -> str:
    """Fallback descriptor when a note has no `summary`: its first H1, else first line."""
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            body = text[end + 4:]
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    for line in body.splitlines():
        if line.strip():
            return line.strip()[:120]
    return ""


def note_descriptor(md: Path) -> tuple[str, str, str, bool]:
    """Return (title, summary, status, has_summary) for a note file."""
    text = md.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    title = str(fm.get("title") or md.stem)
    status = str(fm.get("status") or "")
    summary = fm.get("summary")
    if summary:
        return title, str(summary), status, True
    return title, first_heading_or_line(text), status, False


def dir_summary(directory: Path) -> str:
    """A directory's summary comes from the frontmatter of its own index.md."""
    idx = directory / "index.md"
    if not idx.exists():
        return ""
    fm = parse_frontmatter(idx.read_text(encoding="utf-8", errors="replace"))
    return str(fm.get("summary") or "")


def build_block(directory: Path) -> tuple[str, list[Path]]:
    """Build the auto-index markdown block for one directory.

    Returns (block_text, notes_missing_summary).
    """
    subdirs = sorted(
        d for d in directory.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name not in SKIP_DIRS
    )
    notes = sorted(
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in NOTE_EXTS and f.name not in SKIP_FILES
    )
    others = sorted(
        f for f in directory.iterdir()
        if f.is_file()
        and f.suffix.lower() not in NOTE_EXTS
        and f.name not in SKIP_FILES
        and not f.name.startswith(".")
    )

    lines: list[str] = []
    missing: list[Path] = []

    if subdirs:
        lines.append("### Areas")
        lines.append("")
        for d in subdirs:
            s = dir_summary(d)
            tail = f" — {s}" if s else " — _(no area summary yet)_"
            href = f"{quote(d.name)}/index.md"
            lines.append(f"- [`{d.name}/`]({href}){tail}")
        lines.append("")

    if notes:
        lines.append("### Notes")
        lines.append("")
        for n in notes:
            title, summary, status, has_summary = note_descriptor(n)
            if not has_summary:
                missing.append(n)
            badge = f" _({status})_" if status else ""
            desc = summary if summary else "_(no summary yet)_"
            lines.append(f"- [{title}]({quote(n.name)}){badge} — {desc}")
        lines.append("")

    if others:
        lines.append("### Files")
        lines.append("")
        for f in others:
            lines.append(f"- [`{f.name}`]({quote(f.name)})")
        lines.append("")

    if not (subdirs or notes or others):
        lines.append("_(empty)_")
        lines.append("")

    block = "\n".join(lines).rstrip() + "\n"
    return block, missing


def render_index(directory: Path, block: str, existing: str | None) -> str:
    """Insert/replace the auto-index block, preserving any human-written content.

    Normalizes surrounding blank lines so repeated runs are idempotent (no newline
    creep) while keeping any human-written regions above/below the markers intact.
    """
    wrapped = f"{BEGIN}\n\n{block.rstrip()}\n\n{END}"

    if existing and BEGIN in existing and END in existing:
        head = existing.split(BEGIN, 1)[0].rstrip("\n")
        tail = existing.split(END, 1)[1].strip("\n")
        parts = [p for p in (head, wrapped, tail) if p]
        return "\n\n".join(parts) + "\n"

    # No existing managed block.
    if existing:
        # Append the block to whatever was there rather than discarding it.
        return f"{existing.rstrip()}\n\n{wrapped}\n"
    title = directory.name or "knowledge base"
    return f"# {title} — index\n\n{wrapped}\n"


def walk(root: Path):
    """Yield every directory under root (inclusive), skipping SKIP_DIRS."""
    yield root
    for d in sorted(p for p in root.rglob("*") if p.is_dir()):
        if any(part in SKIP_DIRS or part.startswith(".") for part in d.relative_to(root).parts):
            continue
        yield d


def main() -> int:
    ap = argparse.ArgumentParser(description="Regenerate knowledge-base index.md files.")
    ap.add_argument("root", nargs="?", default=".", help="Root of the knowledge base (default: .)")
    ap.add_argument("--check", action="store_true", help="Exit 1 if any index is stale; write nothing.")
    ap.add_argument("--report", action="store_true", help="Print notes that are missing a summary.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    stale: list[Path] = []
    all_missing: list[Path] = []
    written = 0

    for directory in walk(root):
        block, missing = build_block(directory)
        all_missing.extend(missing)
        idx = directory / "index.md"
        existing = idx.read_text(encoding="utf-8", errors="replace") if idx.exists() else None
        new_content = render_index(directory, block, existing)

        if existing != new_content:
            if args.check:
                stale.append(idx)
            else:
                idx.write_text(new_content, encoding="utf-8")
                written += 1

    if args.report and all_missing:
        print("Notes missing a `summary` (have the LLM write one into frontmatter):")
        for n in all_missing:
            print(f"  - {n.relative_to(root)}")

    if args.check:
        if stale:
            print("Stale indexes (run without --check to rebuild):")
            for s in stale:
                print(f"  - {s.relative_to(root)}")
            return 1
        print("All indexes up to date.")
        return 0

    print(f"Rebuilt {written} index.md file(s) under {root}.")
    if all_missing:
        print(f"{len(all_missing)} note(s) still need a summary — run with --report to list them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
