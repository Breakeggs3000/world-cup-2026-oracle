# Git workflow policy

## Commits

- Create commits **only** when the user explicitly asks.
- Write commit messages that explain **why**, not just what changed.
- Do not commit `workspace/scratch/`, `workspace/sessions/`, or secrets.

## Branches and PRs

- Create pull requests only when the user asks.
- Use `gh` for GitHub operations when available.
- Do not force-push to `main` or `master`.

## Amend and hooks

- Avoid `git commit --amend` unless explicitly requested and safe (unpushed, your commit).
- Never skip pre-commit hooks unless the user explicitly requests it.
- If a hook fails, fix the issue and make a **new** commit — do not amend a failed commit.

## Config

- Never change git config (user.name, user.email, etc.).
