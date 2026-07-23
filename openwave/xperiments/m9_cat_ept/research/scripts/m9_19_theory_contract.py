"""Run the deterministic M9.19 simulation-theory contract study."""
from openwave.xperiments.m9_cat_ept.theory_contract import result_to_json, run_theory_contract_study

def main() -> int:
    result = run_theory_contract_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__": raise SystemExit(main())
