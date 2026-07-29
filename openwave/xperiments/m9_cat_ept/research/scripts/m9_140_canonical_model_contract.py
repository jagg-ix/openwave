from __future__ import annotations

from openwave.xperiments.m9_cat_ept.canonical_particle_model_m140 import (
    result_to_json,
    run_canonical_model_contract,
)


if __name__ == "__main__":
    result = run_canonical_model_contract()
    print(result_to_json(result), end="")
    if not result["passed"]:
        raise SystemExit(1)
