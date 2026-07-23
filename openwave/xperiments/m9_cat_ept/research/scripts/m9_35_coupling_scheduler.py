"""Run m9_35_coupling_scheduler."""
from openwave.xperiments.m9_cat_ept.coupling_scheduler import result_to_json, run_scheduler_study

def main() -> int:
    result=run_scheduler_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
