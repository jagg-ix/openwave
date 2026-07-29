from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.pauli_hartree_u1_carrier_m141 import (
    run_pauli_hartree_u1_campaign,
)


if __name__ == "__main__":
    result = run_pauli_hartree_u1_campaign()
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
    if not result["passed"]:
        raise SystemExit(1)
