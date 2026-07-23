"""Run the frozen M9.3 field-to-probability and coarse-graining study."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.entropic_clock import (
    run_entropic_clock_study,
)


def main() -> int:
    result = run_entropic_clock_study()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
