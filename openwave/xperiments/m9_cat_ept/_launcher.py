"""Launcher for the validated M9 scalar, radial, and transverse sectors."""

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
    parser = argparse.ArgumentParser(description="M9 CAT/EPT research instrumentation")
    parser.add_argument("--list", action="store_true", help="list deterministic presets")
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


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list:
        _print_list()
        return 0
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
