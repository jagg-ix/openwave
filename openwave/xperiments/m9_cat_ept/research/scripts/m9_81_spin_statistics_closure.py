from openwave.xperiments.m9_cat_ept.spin_statistics_closure import (
    result_to_json,
    run_spin_statistics_closure,
)

print(result_to_json(run_spin_statistics_closure()), end="")
