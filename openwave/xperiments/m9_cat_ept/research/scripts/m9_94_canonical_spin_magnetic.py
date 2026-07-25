"""Run the M9.94 canonical particle spin and magnetic-moment bridge."""
from openwave.xperiments.m9_cat_ept.canonical_spin_magnetic_bridge import (
    result_to_json,
    run_canonical_spin_magnetic_bridge,
)


if __name__ == "__main__":
    print(result_to_json(run_canonical_spin_magnetic_bridge()), end="")
