from openwave.xperiments.m9_cat_ept.physical_calibration_ledger_v3 import (
    result_to_json,
    run_physical_calibration_ledger_v3,
)


if __name__ == "__main__":
    print(result_to_json(run_physical_calibration_ledger_v3()), end="")
