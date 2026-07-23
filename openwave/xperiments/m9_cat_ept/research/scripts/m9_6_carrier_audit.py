"""Run the deterministic M9.6 scalar-carrier capability audit."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.carrier_audit import audit_scalar_carrier


def main() -> int:
    result = audit_scalar_carrier()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
