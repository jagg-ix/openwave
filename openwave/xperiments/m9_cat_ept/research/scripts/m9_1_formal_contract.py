"""Run the M9.1 version-pinned CAT/EPT formal conformance suite."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.formal_contract import run_conformance_suite


def main() -> int:
    result = run_conformance_suite()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
