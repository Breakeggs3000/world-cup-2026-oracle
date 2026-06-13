# Copilot instructions

This project uses the **agent workspace** layout.

## Structure

- Application code lives in `src/` (empty in template repos).
- Read `AGENTS.md` for the operating model.
- Project context: `context/`; memory: `memory/facts/`.
- Universal Cursor rules: `~/.cursor/rules/` (not duplicated per project).

## Code style

- Prefer small, focused changes over large refactors.
- Match existing patterns in the file and surrounding module.
- Add comments only for non-obvious logic.

## Safety

- Do not suggest committing secrets or `.env` files.
- Do not suggest destructive git operations.
- Ask before assuming product decisions not in `context/project/overview.md`.
