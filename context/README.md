# Context

Durable project knowledge that agents should read and update. Unlike `memory/facts/`, context is curated and human-reviewed.

## Layout

```
context/
├── project/           # What we're building and why
├── architecture/      # Design decisions (ADRs)
└── domain/            # Business terms and rules
```

## Guidelines

- Keep documents short and current; delete stale sections.
- Prefer links to code in `src/` over duplicating implementation detail.
- Significant design changes go in `architecture/decisions.md` using the ADR template.
