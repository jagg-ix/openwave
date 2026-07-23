"""Run m9_39_lepton_hierarchy_audit."""
from openwave.xperiments.m9_cat_ept.lepton_hierarchy_audit import result_to_json, run_lepton_hierarchy_audit

def main() -> int:
    result=run_lepton_hierarchy_audit(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
