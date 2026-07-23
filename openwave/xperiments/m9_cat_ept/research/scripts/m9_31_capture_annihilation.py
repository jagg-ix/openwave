"""Run m9_31_capture_annihilation."""
from openwave.xperiments.m9_cat_ept.capture_annihilation import result_to_json, run_capture_annihilation_study

def main() -> int:
    result=run_capture_annihilation_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
