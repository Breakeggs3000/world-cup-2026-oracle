# Policies

Operational rules all agents must follow.

## Three layers

| Layer | Location | Examples |
|-------|----------|----------|
| User | `~/.cursor/rules/` | Git safety, core principles |
| Template / project | `policies/` here | Safety, git workflow, communication (for all orchestrators) |
| Project-only | `.cursor/rules/` | Stack-specific conventions |

Cursor loads user rules globally. `policies/` remains the source of truth for CrewAI and non-Cursor agents.

| Policy | File |
|--------|------|
| Safety | [safety.md](./safety.md) |
| Git workflow | [git-workflow.md](./git-workflow.md) |
| Communication | [communication.md](./communication.md) |

Policies are normative: when in doubt, follow the stricter rule.
