# Memory

Cross-session facts agents discover and should reuse. Lighter-weight than `context/` — agents may write here; humans periodically curate into `context/`.

## Layout

```
memory/
└── facts/     # One file per fact or topic: <slug>.md
```

## Fact file format

```markdown
# <Title>

**Learned:** YYYY-MM-DD  
**Source:** task, file, or conversation reference

<Concise fact or constraint agents need later>
```

## Maintenance

- Keep facts atomic — one idea per file.
- Delete or merge duplicates during review.
- Promote stable facts to `context/` when they become official project knowledge.
