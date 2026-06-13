#!/usr/bin/env python3
"""Train baseline model and persist versioned artifacts to workspace/artifacts/models/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.model.artifacts import DEFAULT_MODEL_ID, train_and_save_model  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and save a model artifact bundle.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Registry id for this model")
    parser.add_argument(
        "--set-active",
        action="store_true",
        default=True,
        help="Mark this model as active in registry (default: true)",
    )
    parser.add_argument("--no-set-active", action="store_false", dest="set_active")
    parser.add_argument("--tag", action="append", default=[], help="Tag(s) for registry metadata")
    parser.add_argument("--notes", default="", help="Free-form notes stored in metadata")
    args = parser.parse_args()

    tags = args.tag or ["baseline"]
    bundle, report = train_and_save_model(
        model_id=args.model_id,
        set_active=args.set_active,
        tags=tags,
        notes=args.notes,
    )
    test = report["test"]
    print(f"Saved model: {bundle.model_id}")
    print(
        f"Test accuracy: {test['accuracy']:.1%} | "
        f"RPS: {test['rps']:.3f} | "
        f"beats naive by: {report['beats_naive_by']:.1%}"
    )
    print(f"Artifacts: workspace/artifacts/models/{bundle.model_id}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
