"""Run the deterministic M9.7b3 constrained dynamic qualification."""

from __future__ import annotations

from pathlib import Path

from openwave.xperiments.m9_cat_ept.dirac_electrostatic_dynamics_3d import (
    write_result,
)


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "data" / (
        "m9_7b3_dirac_electrostatic_dynamics_result.json"
    )
    result = write_result(output)
    if not result["passed"]:
        raise SystemExit("M9.7b3 acceptance gate failed")
    print(output)


if __name__ == "__main__":
    main()
