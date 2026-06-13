# Agent Operating Guide

This repository uses the **agent workspace** layout. Read this file first at the start of every session.

> **Template repo:** If you are in a generated project, `context/project/overview.md` describes *that* product. This file defines *how* agents work in any workspace cloned from the template.

## Quick orientation

| Path | Purpose |
|------|---------|
| `agents/` | Role definitions, crew compositions, agent registry |
| `context/` | Durable project knowledge agents should reuse |
| `tasks/` | Task specs, templates, and backlog |
| `workspace/` | Scratch work, artifacts, and session outputs |
| `memory/` | Long-lived facts learned across sessions |
| `policies/` | Safety, git, and communication rules |
| `tools/` | Scripts and utilities agents may invoke |
| `src/` | Application source code |
| `.cursor/rules/` | Project-specific Cursor rules (stack, conventions) |

## Session workflow

1. **Load context** — Read `context/project/overview.md` and any relevant `context/` docs.
2. **Check memory** — Scan `memory/facts/` for prior decisions or constraints.
3. **Pick a task** — Take work from `tasks/backlog/` or follow the user’s prompt.
4. **Assume a role** — Use `agents/registry.yaml` and `agents/roles/` to adopt the right persona.
5. **Work in the right place** — Draft in `workspace/scratch/`; commit-worthy code in `src/`.
6. **Record outcomes** — Update `memory/facts/`, `context/architecture/decisions.md`, or task status as needed.

## Agent roles

| Role | File | When to use |
|------|------|-------------|
| Researcher | `agents/roles/researcher.md` | Explore, gather facts, compare options |
| Implementer | `agents/roles/implementer.md` | Write code, apply focused changes |
| Reviewer | `agents/roles/reviewer.md` | Review diffs, find risks, suggest fixes |

For multi-agent work, compose crews from `agents/crews/`.

## Operating principles

- **Minimize scope** — Smallest correct change that solves the task.
- **Reuse before reinventing** — Search `src/`, `context/`, and `memory/` first.
- **Separate ephemeral from durable** — Scratch in `workspace/scratch/` (gitignored); knowledge in `context/` or `memory/`.
- **Follow policies** — `policies/safety.md`, `policies/git-workflow.md`, `policies/communication.md`.
- **Ask when blocked** — Do not guess at secrets, destructive actions, or ambiguous product decisions.

## Platform-specific entry points

- **Cursor**: This file + user rules in `~/.cursor/rules/` + project rules in `.cursor/rules/`
- **Cursor onboarding skill**: `~/.cursor/skills/agent-workspace-onboard/`
- **GitHub Copilot**: `.github/copilot-instructions.md`
- **CrewAI / custom orchestrators**: `agents/registry.yaml` + `agents/crews/`

## What not to do

- Do not commit `.env`, credentials, or `workspace/scratch/` contents.
- Do not run destructive git commands unless explicitly requested.
- Do not create commits or pull requests unless the user asks.
- Do not add unrelated refactors while completing a scoped task.
- Do not mix multiple unrelated products in one repo — generate a new workspace per project.
