# Tasks

Work items for agents and humans. Each task should be actionable without extra context.

## Layout

```
tasks/
├── templates/task.md    # Copy this for new work
└── backlog/             # Active and pending tasks
```

## Workflow

1. Create `tasks/backlog/<id>-<slug>.md` from the template.
2. Assign a role or crew from `agents/registry.yaml`.
3. On completion, move to `tasks/done/` (create when needed) or mark status in the file.

## Naming

Use `TASK-001-short-description.md` or a date prefix: `2026-06-13-feature-x.md`.
