#!/usr/bin/env python3
"""Emit FastAPI OpenAPI schema into packages/api-contract/openapi.yaml ."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
_TARGET = _ROOT / "packages" / "api-contract" / "openapi.yaml"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(_ROOT / "apps" / "query-service"))

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        print("Install PyYAML: pip install PyYAML")
        return 2

    from app.main import app

    openapi = app.openapi()

    dumped = yaml.safe_dump(
        openapi,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=float("inf"),
    )
    if args.dry_run:
        print(dumped[:2000])
        return 0
    _TARGET.parent.mkdir(parents=True, exist_ok=True)
    _TARGET.write_text(dumped, encoding="utf-8")
    print(f"Wrote {_TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
