from openwave.xperiments.m9_cat_ept.static_dynamic_bridge import result_to_json, run_static_dynamic_bridge_study

def main()->int:
    result=run_static_dynamic_bridge_study(); print(result_to_json(result),end="")
    return 0 if result["passed"] else 1
if __name__=="__main__": raise SystemExit(main())
