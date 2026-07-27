from openwave.xperiments.m9_cat_ept.model_registration_current import run_model_registration_study, result_to_json

print(result_to_json(run_model_registration_study()), end="")
