"""Seed JSON fixture provider."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.data.loader import WC2026_PATH, load_wc2026_fixtures_from_json


class SeedJsonProvider:
    name = "seed"

    def __init__(self, path: Path | None = None):
        self.path = path or WC2026_PATH

    def fetch_fixtures(self) -> list[dict[str, Any]]:
        return load_wc2026_fixtures_from_json(self.path)
