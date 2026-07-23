"""Run the deterministic M9.21 cross-theory simulation qualification."""
from openwave.xperiments.m9_cat_ept.simulation_qualification import result_to_json, run_simulation_qualification_study

def main() -> int:
    result = run_simulation_qualification_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__": raise SystemExit(main())
