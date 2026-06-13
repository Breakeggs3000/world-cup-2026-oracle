# Tools

Shared scripts and utilities agents may run.

## Project generator

Create a new vibe-coding repo (sibling to `pilot101` by default):

```powershell
.\tools\scripts\new-agent-project.ps1 my-vibe-app -Purpose "What you're building" -InitGit
```

See [TEMPLATE.md](../TEMPLATE.md) for options and the three-layer config model.

## Layout

```
tools/
└── scripts/
    ├── new-agent-project.py
    └── new-agent-project.ps1
```

## Adding a tool

1. Place script in `tools/scripts/<name>.<ext>`.
2. Document usage in a comment header or this README.
3. Prefer cross-platform commands when possible.

## Agent usage

- Read the script before running it.
- Do not pass secrets on the command line; use environment variables.
- Capture output to `workspace/artifacts/` when the result should persist.
