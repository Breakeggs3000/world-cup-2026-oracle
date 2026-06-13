#!/usr/bin/env python3
"""Scaffold a new agent workspace from the pilot101 template."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

# Paths and names excluded when copying template → project
SKIP_NAMES = {
    ".git",
    "__pycache__",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
}

# Template-only files — not copied to new projects
TEMPLATE_ONLY_FILES = {
    "TEMPLATE.md",
}

# Directories cleared after copy (keep .gitkeep only)
CLEAR_GLOBS = (
    "workspace/scratch/*",
    "memory/facts/*",
    "tasks/backlog/*",
    "workspace/artifacts/research/*",
    "workspace/artifacts/reviews/*",
)

OVERVIEW_TEMPLATE = """# Project overview

> Agents read this at session start.

## Name

{project_name}

## Purpose

{project_purpose}

## Current status

Greenfield — workspace scaffold ready; application code not yet started.

## Tech stack

_To be decided._ Document choices here before agents implement in `src/`.

## Repository map

| Path | Contents |
|------|----------|
| `src/` | Application source |
| `agents/` | Role and crew definitions |
| `tasks/` | Work backlog |
| `workspace/` | Scratch and artifacts |

## Success criteria

_Define what "done" looks like for this product._

## Contacts / ownership

_Optional._
"""

README_TEMPLATE = """# {project_name}

Generated from the [agent workspace template](../pilot101) (pilot101).

## Getting started

1. Read [AGENTS.md](./AGENTS.md).
2. Fill in [context/project/overview.md](./context/project/overview.md).
3. Build in `src/`.
4. Track work in `tasks/backlog/`.

## Agent workspace

This repo uses the agent workspace layout. Universal Cursor rules live in `~/.cursor/rules/`; project-specific rules go in `.cursor/rules/`.
"""


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in SKIP_NAMES for part in rel.parts):
        return True
    if rel.name in TEMPLATE_ONLY_FILES:
        return True
    return False


def copy_template(template_root: Path, dest: Path, dry_run: bool) -> None:
    if dest.exists():
        raise FileExistsError(f"Destination already exists: {dest}")

    if dry_run:
        print(f"[dry-run] Would create: {dest}")
        return

    dest.mkdir(parents=True, exist_ok=False)

    for src in template_root.rglob("*"):
        if src == template_root:
            continue
        if should_skip(src, template_root):
            continue
        rel = src.relative_to(template_root)
        target = dest / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)


def clear_workspace_state(project_root: Path, dry_run: bool) -> None:
    for pattern in CLEAR_GLOBS:
        for path in project_root.glob(pattern):
            if path.name == ".gitkeep":
                continue
            if dry_run:
                print(f"[dry-run] Would remove: {path}")
            else:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)


def write_project_files(
    project_root: Path,
    project_name: str,
    project_slug: str,
    project_purpose: str,
    dry_run: bool,
) -> None:
    overview = OVERVIEW_TEMPLATE.format(
        project_name=project_name,
        project_purpose=project_purpose or "_Describe what you are building._",
    )
    readme = README_TEMPLATE.format(project_name=project_name)
    config = {
        "kind": "agent-workspace-project",
        "version": "1",
        "name": project_name,
        "slug": project_slug,
        "created": date.today().isoformat(),
        "template": "pilot101",
    }

    files = {
        "context/project/overview.md": overview,
        "README.md": readme,
        "template.config.json": json.dumps(config, indent=2) + "\n",
    }

    for rel, content in files.items():
        path = project_root / rel
        if dry_run:
            print(f"[dry-run] Would write: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


def init_git(project_root: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] Would run: git init in {project_root}")
        return
    subprocess.run(["git", "init"], cwd=project_root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new agent workspace project from the pilot101 template."
    )
    parser.add_argument("name", help="Project name (used for directory and docs)")
    parser.add_argument(
        "--parent",
        type=Path,
        default=None,
        help="Parent directory for the new project (default: parent of template root)",
    )
    parser.add_argument(
        "--purpose",
        default="",
        help="One-line purpose for context/project/overview.md",
    )
    parser.add_argument(
        "--init-git",
        action="store_true",
        help="Run git init in the new project",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without creating files",
    )
    args = parser.parse_args()

    template_root = Path(__file__).resolve().parents[2]
    if not (template_root / "AGENTS.md").exists():
        print("Error: run from pilot101 template (AGENTS.md not found).", file=sys.stderr)
        return 1

    parent = args.parent or template_root.parent
    slug = slugify(args.name)
    dest = parent / slug

    try:
        copy_template(template_root, dest, args.dry_run)
        if not args.dry_run:
            clear_workspace_state(dest, args.dry_run)
        write_project_files(dest, args.name, slug, args.purpose, args.dry_run)
        if args.init_git:
            init_git(dest, args.dry_run)
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"Error: git init failed: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"[dry-run] Ready: {dest}")
    else:
        print(f"Created agent workspace: {dest}")
        print("Next steps:")
        print(f"  cd {dest}")
        print("  Edit context/project/overview.md")
        print("  Start building in src/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
