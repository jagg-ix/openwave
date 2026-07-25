from openwave.xperiments.m9_cat_ept.dirac_ehrenfest_diagnostics import (
    result_to_json,
    run_dirac_ehrenfest_diagnostics,
)


if __name__ == "__main__":
    print(result_to_json(run_dirac_ehrenfest_diagnostics()), end="")
