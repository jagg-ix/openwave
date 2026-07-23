"""Run the deterministic M9.7b2 coupled stationary gate."""

from __future__ import annotations

from pathlib import Path

from openwave.xperiments.m9_cat_ept.dirac_electrostatic_3d import write_result


def main() -> int:
    destination = (
        Path(__file__).parents[1]
        / "data"
        / "m9_7b2_dirac_electrostatic_result.json"
    )
    result = write_result(destination)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
