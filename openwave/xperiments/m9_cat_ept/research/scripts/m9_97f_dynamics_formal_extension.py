from openwave.xperiments.m9_cat_ept.formalization_dynamics_extension import (
    result_to_json,
    run_dynamics_formal_extension_study,
)


if __name__ == "__main__":
    print(result_to_json(run_dynamics_formal_extension_study()), end="")
