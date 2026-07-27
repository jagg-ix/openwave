from openwave.xperiments.m9_cat_ept.model_conformance_current import (
    result_to_json,
    run_conformance_study,
)

print(result_to_json(run_conformance_study()), end="")
