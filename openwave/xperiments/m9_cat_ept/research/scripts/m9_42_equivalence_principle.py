"""Run M9.42 equivalence principle suite."""
from openwave.xperiments.m9_cat_ept.equivalence_principle import result_to_json, run_equivalence_principle_study

def main() -> int:
    result = run_equivalence_principle_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
