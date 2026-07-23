"""Run the frozen M9.4 nonlinear localization decision gate."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.localized_particle import (
    run_localization_study,
)


def main() -> int:
    result = run_localization_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
