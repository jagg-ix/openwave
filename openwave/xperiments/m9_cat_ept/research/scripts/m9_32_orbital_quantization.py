"""Run m9_32_orbital_quantization."""
from openwave.xperiments.m9_cat_ept.orbital_quantization import result_to_json, run_orbital_quantization_study

def main() -> int:
    result=run_orbital_quantization_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
