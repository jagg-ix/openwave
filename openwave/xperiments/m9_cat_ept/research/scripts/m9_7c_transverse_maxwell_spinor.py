"""Run the deterministic M9.7c transverse Maxwell--spinor qualification."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.transverse_maxwell_spinor import (
    run_transverse_study,
)


def main() -> None:
    print(json.dumps(run_transverse_study(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
