#!/usr/bin/env python3
"""Download martj42 international results CSV into data cache."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = BACKEND_ROOT / "app" / "data" / "cache"
OUTPUT = CACHE_DIR / "results.csv"


def main() -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {URL} ...")
    response = httpx.get(URL, follow_redirects=True, timeout=120.0)
    response.raise_for_status()
    OUTPUT.write_bytes(response.content)
    lines = OUTPUT.read_text(encoding="utf-8").count("\n")
    print(f"Saved {OUTPUT} ({lines:,} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
