"""Run the deterministic M9.19 calibration-contract qualification."""
from openwave.xperiments.m9_cat_ept.calibration_contract import (
    result_to_json,
    run_calibration_contract_study,
)

def main() -> int:
    result = run_calibration_contract_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
