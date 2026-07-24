"""Run m9_48_stability_campaign."""
from openwave.xperiments.m9_cat_ept.stability_campaign_3d import result_to_json, run_long_horizon_stability_study

def main() -> int:
    result=run_long_horizon_stability_study(); print(result_to_json(result),end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
