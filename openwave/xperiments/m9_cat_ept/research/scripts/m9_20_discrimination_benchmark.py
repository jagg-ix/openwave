"""Run the deterministic M9.20 discrimination benchmark."""
from openwave.xperiments.m9_cat_ept.discrimination_benchmark import (
    result_to_json,
    run_discrimination_benchmark,
)

def main() -> int:
    result = run_discrimination_benchmark()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
