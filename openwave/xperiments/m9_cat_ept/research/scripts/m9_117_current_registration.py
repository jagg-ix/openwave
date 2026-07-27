from openwave.xperiments.m9_cat_ept.model_registration_m117 import (
    result_to_json,
    run_model_registration_study,
)

print(result_to_json(run_model_registration_study()), end="")
