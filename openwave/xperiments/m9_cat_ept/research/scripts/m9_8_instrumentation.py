"""Run the deterministic M9.8 instrumentation qualification."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.instrumentation import run_instrumentation_study


def main() -> int:
    result = run_instrumentation_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
