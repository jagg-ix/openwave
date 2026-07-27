from openwave.xperiments.m9_cat_ept.calibration_holdout_protocol import (
    result_to_json,
    run_calibration_holdout_protocol,
)

print(result_to_json(run_calibration_holdout_protocol()), end="")
