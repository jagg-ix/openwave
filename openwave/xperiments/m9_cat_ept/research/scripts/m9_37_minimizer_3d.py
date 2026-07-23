"""Run m9_37_minimizer_3d."""
from openwave.xperiments.m9_cat_ept.minimizer_3d import result_to_json, run_minimizer_continuation_study

def main() -> int:
    result=run_minimizer_continuation_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
