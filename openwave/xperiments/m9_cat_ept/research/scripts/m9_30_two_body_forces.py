"""Run M9.30 two-body force kernels."""
from openwave.xperiments.m9_cat_ept.two_body_forces import result_to_json, run_two_body_force_study

def main()->int:
    result=run_two_body_force_study(); print(result_to_json(result),end=""); return 0 if result["passed"] else 1
if __name__=="__main__": raise SystemExit(main())
