"""Run M9.59 action-derived binding discrimination."""
from openwave.xperiments.m9_cat_ept.action_derived_binding import result_to_json,run_binding_discrimination

def main()->int:
    result=run_binding_discrimination(); print(result_to_json(result),end=""); return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
