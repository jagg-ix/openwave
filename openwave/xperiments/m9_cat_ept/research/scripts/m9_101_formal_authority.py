from openwave.xperiments.m9_cat_ept.formalization_m101_extension import (
    result_to_json,
    run_formalization_m101_extension,
)

if __name__ == "__main__":
    print(result_to_json(run_formalization_m101_extension()), end="")
