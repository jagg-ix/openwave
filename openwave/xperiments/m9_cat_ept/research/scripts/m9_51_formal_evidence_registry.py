"""Run M9.51 formal evidence registry."""
from openwave.xperiments.m9_cat_ept.formal_evidence_registry import result_to_json,run_formal_evidence_study

def main()->int:
    result=run_formal_evidence_study(); print(result_to_json(result),end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
