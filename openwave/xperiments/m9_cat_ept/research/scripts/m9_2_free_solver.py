"""Run the M9.2 free Gaussian-packet refinement benchmark."""

from __future__ import annotations

from dataclasses import asdict
import json

from openwave.xperiments.m9_cat_ept.free_solver import run_refinement_study


def main() -> int:
    result = run_refinement_study()
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
