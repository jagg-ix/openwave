"""Run M9.40 confinement sector."""
from openwave.xperiments.m9_cat_ept.confinement_sector import result_to_json, run_confinement_study

def main() -> int:
    result = run_confinement_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
