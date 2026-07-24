"""Run m9_53_fokker_planck."""
from openwave.xperiments.m9_cat_ept.fokker_planck_bridge import result_to_json,run_fokker_planck_study

def main()->int:
    result=run_fokker_planck_study();print(result_to_json(result),end="");return 0 if result["passed"] else 1

if __name__=="__main__":raise SystemExit(main())
