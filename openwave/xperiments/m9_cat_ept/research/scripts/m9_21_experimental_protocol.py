"""Run the deterministic M9.21 experimental-protocol qualification."""
from openwave.xperiments.m9_cat_ept.experimental_protocol import (
    result_to_json,
    run_experimental_protocol_study,
)

def main() -> int:
    result = run_experimental_protocol_study()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
