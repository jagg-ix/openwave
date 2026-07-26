"""Generate or verify the four M9.101 quantitative result snapshots."""
from __future__ import annotations

import argparse

from openwave.xperiments.m9_cat_ept.m101_reproducibility_contract import (
    result_to_json,
    run_m101_reproducibility_contract,
    verify_snapshot_bundle,
    write_snapshot_bundle,
)


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser()
    mode = command.add_mutually_exclusive_group()
    mode.add_argument("--write", metavar="DIRECTORY")
    mode.add_argument("--verify", metavar="DIRECTORY")
    return command


def main() -> int:
    arguments = parser().parse_args()
    if arguments.write:
        result = write_snapshot_bundle(arguments.write)
        print(result_to_json(result), end="")
        return 0
    if arguments.verify:
        result = verify_snapshot_bundle(arguments.verify)
        print(result_to_json(result), end="")
        return 0 if result["passed"] else 1
    result = run_m101_reproducibility_contract()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
