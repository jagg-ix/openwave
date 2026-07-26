from openwave.xperiments.m9_cat_ept.model_registration_m101 import (
    result_to_json,
    run_model_registration_study,
)

if __name__ == "__main__":
    print(result_to_json(run_model_registration_study()), end="")
