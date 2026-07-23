"""Run the deterministic M9.10 two-dimensional Maxwell--Dirac study."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.planar_2d_maxwell_dirac import (
    run_planar_2d_study,
)


def main() -> int:
    result = run_planar_2d_study()
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
