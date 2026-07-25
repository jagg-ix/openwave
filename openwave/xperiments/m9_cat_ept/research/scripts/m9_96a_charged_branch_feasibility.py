from openwave.xperiments.m9_cat_ept.charged_branch_feasibility import (
    result_to_json,
    run_charged_branch_feasibility,
)


if __name__ == "__main__":
    print(result_to_json(run_charged_branch_feasibility()), end="")
