"""Run the deterministic M9.7b1 electrostatic gauge qualification gate."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.electrostatic_gauge_3d import (
    run_electrostatic_gauge_study,
)


def main() -> int:
    result = run_electrostatic_gauge_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
