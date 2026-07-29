from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.global_inference_statistics_emwave_m137 import (
    run_m137_global_authority,
)


if __name__ == "__main__":
    report = run_m137_global_authority()
    print(json.dumps(report.payload(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)
