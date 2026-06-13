# Workspace

The agent **working area** — separate from committed source code.

## Layout

```
workspace/
├── scratch/       # Ephemeral drafts (gitignored)
├── artifacts/     # Research, reviews, reports (may commit)
│   ├── research/
│   └── reviews/
└── sessions/      # Optional session logs (gitignored)
```

## Rules

| Directory | Commit? | Use for |
|-----------|---------|---------|
| `scratch/` | No | Spikes, temp scripts, experiments |
| `artifacts/` | Yes (selective) | Deliverables worth keeping |
| `sessions/` | No | Debug logs, raw agent transcripts |

Clean up `scratch/` freely; promote anything valuable to `context/` or `memory/`.
