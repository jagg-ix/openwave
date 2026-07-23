"""Run the deterministic M9.13 coupled three-dimensional qualification."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.spatial_3d_maxwell_dirac import (
    run_spatial_3d_transport_study,
)


def main() -> int:
    result = run_spatial_3d_transport_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
