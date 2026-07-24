"""Run M9.49 unified 3D self-binding/no-go campaign."""
from openwave.xperiments.m9_cat_ept.unified_self_binding_3d import result_to_json, run_unified_self_binding_campaign

def main() -> int:
    result=run_unified_self_binding_campaign(); print(result_to_json(result),end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
