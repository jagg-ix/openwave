from openwave.xperiments.m9_cat_ept.recentered_conservation_closure import (
    result_to_json,
    run_recentered_conservation_closure,
)

print(result_to_json(run_recentered_conservation_closure()), end="")
