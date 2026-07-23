"""Run the deterministic M9.6 scalar-carrier audit."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.carrier_limits import run_scalar_carrier_audit


def main() -> int:
    result = run_scalar_carrier_audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
