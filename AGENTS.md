# Repository guide for agents

This repo packages the `knowledge-base-builder` Agent Skill for distribution
across Cursor, Claude Code, Claude Web, and Claude Cowork.

## Layout

- `knowledge-base-builder/SKILL.md` — the skill itself (source of truth).
- `release-please-config.json`, `.release-please-manifest.json`, `version.txt` —
  release automation via release-please + Conventional Commits.
- `.github/workflows/validate.yml` — validates the skill on PRs/pushes.
- `.github/workflows/release.yml` — cuts releases and uploads
  `knowledge-base-builder.skill`.

## Conventions

- Use Conventional Commits (`feat:`, `fix:`, `docs:`, ...). `feat`/`fix` bump
  the version; merging the release PR publishes `knowledge-base-builder.skill`
  to a
  GitHub Release.
- Keep the `description` in `knowledge-base-builder/SKILL.md` <= 200 chars so it
  uploads to Claude Web/Cowork.
- The version line in `SKILL.md` carries `# x-release-please-version` so
  release-please updates it in place.

## Commands

- `npx skillship validate knowledge-base-builder --profile all`
- `npx skillship package knowledge-base-builder`
- `npx skillship install knowledge-base-builder -a cursor,claude-code`
