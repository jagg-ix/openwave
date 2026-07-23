"""Run the deterministic M9.14 three-dimensional localization decision."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.spatial_3d_localization_decision import (
    run_spatial_3d_localization_decision,
)


def main() -> int:
    result = run_spatial_3d_localization_decision()
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
