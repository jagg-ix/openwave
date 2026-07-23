"""Run M9.28 intrinsic-clock reduction."""
from openwave.xperiments.m9_cat_ept.intrinsic_clock_reduction import result_to_json, run_intrinsic_clock_study

def main() -> int:
    result=run_intrinsic_clock_study(); print(result_to_json(result),end=""); return 0 if result["passed"] else 1
if __name__=="__main__": raise SystemExit(main())
