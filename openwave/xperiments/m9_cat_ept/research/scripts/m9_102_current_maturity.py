from openwave.xperiments.m9_cat_ept.criterion_maturity_m102 import (
    result_to_json,
    run_criterion_maturity_m102,
)


if __name__ == "__main__":
    print(result_to_json(run_criterion_maturity_m102()), end="")
