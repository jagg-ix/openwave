from openwave.xperiments.m9_cat_ept.physical_calibration_ledger_v2 import (
    result_to_json,
    run_physical_calibration_ledger_v2,
)


if __name__ == "__main__":
    print(result_to_json(run_physical_calibration_ledger_v2()), end="")
