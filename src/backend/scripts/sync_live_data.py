#!/usr/bin/env python3
"""Sync WC 2026 fixtures from API-Football (or fallback) into SQLite."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.sync.service import run_sync  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync live WC 2026 fixtures")
    parser.add_argument("--seed", action="store_true", help="Seed DB from JSON only")
    args = parser.parse_args()
    result = run_sync(seed_only=args.seed)
    print(result)
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
