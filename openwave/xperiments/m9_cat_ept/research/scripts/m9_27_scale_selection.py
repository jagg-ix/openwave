"""Run the deterministic m9_27_scale_selection study."""
from openwave.xperiments.m9_cat_ept.scale_selection import result_to_json, run_scale_selection_study

def main() -> int:
    result=run_scale_selection_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
