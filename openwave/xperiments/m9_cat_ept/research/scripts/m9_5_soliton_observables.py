"""Run the deterministic M9.5 soliton observable ledger."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.soliton_observables import (
    run_observable_study,
)


def main() -> int:
    result = run_observable_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
