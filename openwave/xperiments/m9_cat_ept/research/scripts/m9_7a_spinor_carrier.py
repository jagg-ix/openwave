"""Run the deterministic M9.7a nonlinear Dirac/Soler carrier gate."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.spinor_carrier import (
    run_spinor_carrier_study,
)


def main() -> int:
    result = run_spinor_carrier_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
