"""Run M9.41 weak chiral sector."""
from openwave.xperiments.m9_cat_ept.weak_chiral_sector import result_to_json, run_weak_chiral_study

def main() -> int:
    result = run_weak_chiral_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
