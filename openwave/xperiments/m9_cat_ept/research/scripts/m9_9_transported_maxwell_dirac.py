"""Run the deterministic M9.9 transported Maxwell--Dirac qualification."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.transported_maxwell_dirac import (
    run_transport_study,
)


def main() -> int:
    result = run_transport_study()
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
