"""Run the M9.95 canonical particle-pair and formal force bridge."""
from openwave.xperiments.m9_cat_ept.canonical_force_formal_bridge import (
    result_to_json,
    run_canonical_force_formal_bridge,
)


if __name__ == "__main__":
    print(result_to_json(run_canonical_force_formal_bridge()), end="")
