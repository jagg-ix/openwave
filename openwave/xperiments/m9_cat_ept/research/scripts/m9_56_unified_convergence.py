"""Run the M9.56 unified convergence campaign."""
from openwave.xperiments.m9_cat_ept.unified_convergence import (
    result_to_json,
    run_unified_convergence_study,
)


def main() -> int:
    result = run_unified_convergence_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
