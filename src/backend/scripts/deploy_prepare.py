#!/usr/bin/env python3
"""Production bootstrap: fetch data, ensure model artifacts and backtest report exist."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
REPORT_PATH = REPO_ROOT / "workspace" / "artifacts" / "backtest_report.json"


def _run(script: str, *args: str) -> None:
    path = BACKEND_ROOT / "scripts" / script
    print(f">>> {path.name} {' '.join(args)}".strip())
    subprocess.run([sys.executable, str(path), *args], check=True)


def main() -> int:
    sys.path.insert(0, str(BACKEND_ROOT))

    _run("fetch_data.py")

    from app.model.artifacts import try_load_active_bundle

    if try_load_active_bundle() is None:
        print("Model artifacts missing or data fingerprint changed — training…")
        _run("train_model.py")
    else:
        print("Model artifacts OK.")

    if not REPORT_PATH.exists():
        print("Backtest report missing — generating…")
        _run("run_backtest.py")
    else:
        print("Backtest report OK.")

    print("Deploy prepare complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
