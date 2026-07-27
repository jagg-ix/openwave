"""Launcher for current M9 CAT/EPT instrumentation and authority reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from openwave.xperiments.m9_cat_ept.instrumentation import (
    build_panels,
    export_bundle,
    load_presets,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="M9 CAT/EPT instrumentation and current M9.117 authority reports"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="list deterministic presets")
    mode.add_argument(
        "--current-registration",
        action="store_true",
        help="print the stable current registration (M9.117, schema v21)",
    )
    mode.add_argument(
        "--current-conformance",
        action="store_true",
        help="print the current evidence-derived 21-criterion conformance report",
    )
    mode.add_argument(
        "--platform-contract",
        action="store_true",
        help="audit canonical aliases and public M9 documentation for drift",
    )
    parser.add_argument(
        "--preset",
        action="append",
        help="select a preset; may be repeated (default: all)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="rerun the selected deterministic solver instead of loading its ledger",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        help="write JSON and PNG panels to this directory",
    )
    parser.add_argument("--headless", action="store_true", help="do not open a GUI window")
    return parser


def _print_list() -> None:
    for preset in load_presets():
        print(f"{preset.name:24} {preset.task:8} {preset.title}")


def _print_panels(panels) -> None:
    print(json.dumps([panel.to_dict() for panel in panels], indent=2, sort_keys=True))


def _print_current_registration() -> bool:
    from openwave.xperiments.m9_cat_ept.model_registration_current import (
        result_to_json,
        run_model_registration_study,
    )

    result = run_model_registration_study()
    print(result_to_json(result), end="")
    return bool(result["passed"])


def _print_current_conformance() -> bool:
    from openwave.xperiments.m9_cat_ept.model_conformance_current import (
        result_to_json,
        run_conformance_study,
    )

    result = run_conformance_study()
    print(result_to_json(result), end="")
    return bool(result["passed"])


def _print_platform_contract() -> bool:
    from openwave.xperiments.m9_cat_ept.platform_integration_contract import (
        result_to_json,
        run_platform_integration_contract,
    )

    result = run_platform_integration_contract()
    print(result_to_json(result), end="")
    return bool(result["passed"])


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list:
        _print_list()
        return 0
    if args.current_registration:
        return 0 if _print_current_registration() else 1
    if args.current_conformance:
        return 0 if _print_current_conformance() else 1
    if args.platform_contract:
        return 0 if _print_platform_contract() else 1

    panels = build_panels(args.preset, refresh=args.refresh)
    _print_panels(panels)
    if args.export_dir is not None:
        print(json.dumps(export_bundle(panels, args.export_dir), indent=2, sort_keys=True))
    if not args.headless and args.export_dir is None:
        from openwave.xperiments.m9_cat_ept.renderer import show_dashboard

        show_dashboard(panels)
    return 0 if all(panel.passed for panel in panels) else 1


if __name__ == "__main__":
    raise SystemExit(main())
