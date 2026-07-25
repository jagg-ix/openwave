"""Run the M9.93a version-pinned PhysLib contract audit."""
from openwave.xperiments.m9_cat_ept.physlib_contract import (
    result_to_json,
    run_physlib_contract_study,
)


if __name__ == "__main__":
    print(result_to_json(run_physlib_contract_study()), end="")
