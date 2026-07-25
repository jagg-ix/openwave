from openwave.xperiments.m9_cat_ept.gauge_spinor_stationary_current import (
    result_to_json,
    run_gauge_spinor_stationary_feasibility,
)


if __name__ == "__main__":
    print(result_to_json(run_gauge_spinor_stationary_feasibility()), end="")
