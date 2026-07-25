from openwave.xperiments.m9_cat_ept.minimizing_orbit_identification import (
    result_to_json,
    run_minimizing_orbit_identification,
)

print(result_to_json(run_minimizing_orbit_identification()), end="")
