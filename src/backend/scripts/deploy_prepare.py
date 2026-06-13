#!/usr/bin/env python3
"""Production bootstrap: fetch data, ensure model artifacts and backtest report exist."""

from __future__ import annotations

import argparse
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


def build_verify() -> int:
    """Docker/Railway build step — fetch CSV and verify artifacts; never train (OOM risk)."""
    sys.path.insert(0, str(BACKEND_ROOT))
    _run("fetch_data.py")

    from app.model.artifacts import (
        artifacts_match_committed_data,
        get_active_model_id,
        model_bundle_exists,
    )

    model_id = get_active_model_id()
    if not model_id or not model_bundle_exists(model_id):
        raise SystemExit("Model artifacts missing from repo — run scripts/train_model.py locally.")
    if not artifacts_match_committed_data(model_id):
        raise SystemExit(
            "Data fingerprint mismatch after fetch — retrain locally and commit model artifacts."
        )

    if not REPORT_PATH.exists():
        raise SystemExit(
            "backtest_report.json missing — run scripts/run_backtest.py locally and commit it."
        )

    print("Build verify OK.")
    return 0


def full_prepare() -> int:
    """Full bootstrap for Render/native deploy — may train or backtest if artifacts missing."""
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Production deploy bootstrap")
    parser.add_argument(
        "--build",
        action="store_true",
        help="Lightweight verify for Docker build (no train/backtest)",
    )
    args = parser.parse_args()
    if args.build:
        return build_verify()
    return full_prepare()


if __name__ == "__main__":
    sys.exit(main())
