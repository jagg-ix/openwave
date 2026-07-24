"""Run m9_46_quark_color."""
from openwave.xperiments.m9_cat_ept.quark_color_sector import result_to_json, run_quark_color_study

def main() -> int:
    result = run_quark_color_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
