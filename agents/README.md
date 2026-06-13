# Agents

This directory defines **who** can work in the workspace and **how** they are composed for multi-agent runs.

## Layout

```
agents/
├── registry.yaml      # Catalog of available agents/roles
├── roles/             # Role prompts and capabilities
└── crews/             # Multi-agent team compositions
```

## Adding a role

1. Create `agents/roles/<role-name>.md` with goal, constraints, tools, and output format.
2. Register it in `registry.yaml`.
3. Reference it from a crew in `crews/` if needed.

## Orchestrator integration

Custom orchestrators (CrewAI, LangGraph, Cursor Task subagents, etc.) should:

- Load role markdown as system prompts
- Pass `context/` paths as retrieval sources
- Write outputs to `workspace/artifacts/` or `memory/facts/`
- Respect `policies/` for safety and git rules
