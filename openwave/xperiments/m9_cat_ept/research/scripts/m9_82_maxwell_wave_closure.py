from openwave.xperiments.m9_cat_ept.maxwell_wave_closure import (
    result_to_json,
    run_maxwell_wave_closure,
)

print(result_to_json(run_maxwell_wave_closure()), end="")
