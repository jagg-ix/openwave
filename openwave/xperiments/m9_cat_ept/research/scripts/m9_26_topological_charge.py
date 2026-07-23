"""Run the deterministic m9_26_topological_charge study."""
from openwave.xperiments.m9_cat_ept.topological_charge import result_to_json, run_topological_charge_study

def main() -> int:
    result=run_topological_charge_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
