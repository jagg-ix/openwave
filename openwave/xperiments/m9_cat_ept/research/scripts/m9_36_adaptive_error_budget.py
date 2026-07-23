"""Run m9_36_adaptive_error_budget."""
from openwave.xperiments.m9_cat_ept.adaptive_error_budget import result_to_json, run_adaptive_error_budget_study

def main() -> int:
    result=run_adaptive_error_budget_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
