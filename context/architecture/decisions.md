# Architecture decisions

Record significant technical decisions here. Use the template below for each entry.

---

## ADR-000: Agent workspace layout

**Status:** Accepted  
**Date:** 2026-06-13

### Context

The repo needs a structure that supports Cursor, Copilot, and multi-agent orchestration without mixing scratch work, durable knowledge, and source code.

### Decision

Adopt a layered layout:

- `agents/` — roles and crews
- `context/` — curated knowledge
- `memory/` — agent-learned facts
- `workspace/` — ephemeral and generated files
- `src/` — application code
- `AGENTS.md` — single entry point for agents

### Consequences

- Clear boundaries reduce accidental commits of scratch data
- Orchestrators can load `agents/registry.yaml` as machine-readable config
- Humans maintain `context/`; agents may propose updates via PRs

---

## ADR-001: Template repo vs project repos

**Status:** Accepted  
**Date:** 2026-06-13

### Context

Multiple vibe-coding experiments in one repo pollute `context/`, `memory/`, and agent focus. Agent boilerplate (git safety, onboarding) would repeat in every clone unless layered.

### Decision

- Keep `pilot101` as the **canonical template** — no real product code in `src/`.
- **One repo per product**, created via `tools/scripts/new-agent-project.py`.
- **Three config layers:**
  - User: `~/.cursor/rules/`, `~/.cursor/skills/` (universal)
  - Template: this repo (structure, roles, policies)
  - Project: generated repo (`context/`, product-specific `.cursor/rules/`)

### Consequences

- Agents stay scoped to one product context per repo
- Template improvements propagate via generator or cherry-pick
- User-level Cursor rules are not duplicated in each project

---

## Template for new ADRs

```markdown
## ADR-NNN: Title

**Status:** Proposed | Accepted | Superseded  
**Date:** YYYY-MM-DD

### Context
Why this decision is needed.

### Decision
What we chose.

### Consequences
Tradeoffs and follow-ups.
```
