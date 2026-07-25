from openwave.xperiments.m9_cat_ept.spinorial_pair_dynamics_authoritative import (
    result_to_json,
    run_spinorial_pair_dynamics,
)


if __name__ == "__main__":
    print(result_to_json(run_spinorial_pair_dynamics()), end="")
