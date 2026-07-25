"""Run the M9.93c canonical model-registration audit."""
from openwave.xperiments.m9_cat_ept.model_registration import (
    result_to_json,
    run_model_registration_study,
)


if __name__ == "__main__":
    print(result_to_json(run_model_registration_study()), end="")
