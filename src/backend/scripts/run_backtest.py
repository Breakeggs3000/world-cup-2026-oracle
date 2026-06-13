#!/usr/bin/env python3
"""Run walk-forward backtest and write report artifact."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.model.backtest import run_backtest  # noqa: E402


def main() -> int:
    output = REPO_ROOT / "workspace" / "artifacts" / "backtest_report.json"
    report = run_backtest(output)
    test = report["test"]
    print(
        f"Test accuracy: {test['accuracy']:.1%} | "
        f"RPS: {test['rps']:.3f} | "
        f"beats naive by: {report['beats_naive_by']:.1%}"
    )
    print(f"Report written to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
