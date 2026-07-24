"""Run m9_44_thermal_field."""
from openwave.xperiments.m9_cat_ept.thermal_field import result_to_json, run_thermal_field_study

def main() -> int:
    result=run_thermal_field_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
