"""Run m9_47_unified_pde."""
from openwave.xperiments.m9_cat_ept.unified_pde import result_to_json, run_unified_pde_study

def main() -> int:
    result=run_unified_pde_study(); print(result_to_json(result),end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
