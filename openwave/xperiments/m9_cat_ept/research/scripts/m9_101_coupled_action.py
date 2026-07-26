from openwave.xperiments.m9_cat_ept.coupled_gauge_spinor_hartree_action import (
    result_to_json,
    run_coupled_gauge_spinor_hartree_action,
)

if __name__ == "__main__":
    print(result_to_json(run_coupled_gauge_spinor_hartree_action()), end="")
