"""Run the deterministic M9.20 reversible/irreversible integrator study."""
from openwave.xperiments.m9_cat_ept.entropic_integrator import result_to_json, run_entropic_integrator_study

def main() -> int:
    result = run_entropic_integrator_study(); print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__": raise SystemExit(main())
