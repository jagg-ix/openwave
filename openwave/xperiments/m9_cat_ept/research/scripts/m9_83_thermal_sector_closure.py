from openwave.xperiments.m9_cat_ept.thermal_sector_closure import (
    result_to_json,
    run_thermal_sector_closure,
)

print(result_to_json(run_thermal_sector_closure()), end="")
