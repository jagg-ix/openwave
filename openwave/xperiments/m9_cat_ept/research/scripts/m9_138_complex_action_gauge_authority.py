from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.complex_action_gauge_authority_m138 import (
    run_m138_complex_action_gauge_authority,
)


if __name__ == "__main__":
    report = run_m138_complex_action_gauge_authority()
    print(json.dumps(report.payload(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)
