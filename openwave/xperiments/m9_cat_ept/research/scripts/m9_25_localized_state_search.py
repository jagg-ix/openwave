"""Run the deterministic m9_25_localized_state_search study."""
from openwave.xperiments.m9_cat_ept.localized_state_search import result_to_json, run_localized_state_search

def main() -> int:
    result=run_localized_state_search(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
