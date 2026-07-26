from openwave.xperiments.m9_cat_ept.clock_action_rate_calibration import (
    result_to_json,
    run_clock_action_rate_calibration,
)

if __name__ == "__main__":
    print(result_to_json(run_clock_action_rate_calibration()), end="")
