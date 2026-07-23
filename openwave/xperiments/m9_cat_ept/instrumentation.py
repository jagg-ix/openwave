"""Shared M9 preset, ledger, claim-boundary, and export instrumentation."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class MetricSpec:
    key: str
    label: str
    path: str


@dataclass(frozen=True)
class Preset:
    name: str
    title: str
    sector: str
    task: str
    ledger: str
    runner: str
    metrics: tuple[MetricSpec, ...]
    establishes: tuple[str, ...]
    does_not_establish: tuple[str, ...]


@dataclass(frozen=True)
class Panel:
    preset: str
    title: str
    sector: str
    task: str
    passed: bool
    acceptance_passed: int
    acceptance_total: int
    metrics: tuple[tuple[str, float | int | bool], ...]
    establishes: tuple[str, ...]
    does_not_establish: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "preset": self.preset,
            "title": self.title,
            "sector": self.sector,
            "task": self.task,
            "passed": self.passed,
            "acceptance": {
                "passed": self.acceptance_passed,
                "total": self.acceptance_total,
            },
            "metrics": {key: value for key, value in self.metrics},
            "establishes": list(self.establishes),
            "does_not_establish": list(self.does_not_establish),
        }


def package_root() -> Path:
    return Path(__file__).resolve().parent


def preset_manifest_path() -> Path:
    return package_root() / "research" / "presets" / "m9_presets.json"


def ledger_directory() -> Path:
    return package_root() / "research" / "data"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def load_presets(path: Path | None = None) -> tuple[Preset, ...]:
    manifest = _read_json(path or preset_manifest_path())
    if manifest.get("schema") != "openwave.m9.instrumentation-presets.v1":
        raise ValueError("unsupported M9 preset manifest schema")
    presets: list[Preset] = []
    seen: set[str] = set()
    for raw in manifest.get("presets", []):
        name = str(raw["name"])
        if name in seen:
            raise ValueError(f"duplicate preset: {name}")
        seen.add(name)
        metrics = tuple(
            MetricSpec(str(item["key"]), str(item["label"]), str(item["path"]))
            for item in raw.get("metrics", [])
        )
        presets.append(
            Preset(
                name=name,
                title=str(raw["title"]),
                sector=str(raw["sector"]),
                task=str(raw["task"]),
                ledger=str(raw["ledger"]),
                runner=str(raw["runner"]),
                metrics=metrics,
                establishes=tuple(str(item) for item in raw.get("establishes", [])),
                does_not_establish=tuple(
                    str(item) for item in raw.get("does_not_establish", [])
                ),
            )
        )
    if not presets:
        raise ValueError("preset manifest must define at least one preset")
    return tuple(presets)


def preset_map(presets: Sequence[Preset] | None = None) -> dict[str, Preset]:
    return {preset.name: preset for preset in presets or load_presets()}


def select_presets(
    names: Iterable[str] | None,
    presets: Sequence[Preset] | None = None,
) -> tuple[Preset, ...]:
    available = tuple(presets or load_presets())
    if names is None:
        return available
    lookup = preset_map(available)
    selected: list[Preset] = []
    for name in names:
        if name not in lookup:
            choices = ", ".join(sorted(lookup))
            raise KeyError(f"unknown preset {name!r}; choose from {choices}")
        selected.append(lookup[name])
    return tuple(selected)


def resolve_path(payload: Any, path: str) -> Any:
    current = payload
    for token in path.split("."):
        if isinstance(current, Mapping):
            current = current[token]
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            current = current[int(token)]
        else:
            raise KeyError(f"cannot resolve {path!r} at {token!r}")
    return current


def load_ledger(preset: Preset, root: Path | None = None) -> dict[str, Any]:
    path = (root or ledger_directory()) / preset.ledger
    result = _read_json(path)
    if "passed" not in result:
        raise ValueError(f"ledger lacks passed flag: {path}")
    return result


def load_runner(specification: str):
    module_name, separator, attribute = specification.partition(":")
    if not separator or not module_name or not attribute:
        raise ValueError(f"invalid runner specification: {specification}")
    module = import_module(module_name)
    runner = getattr(module, attribute)
    if not callable(runner):
        raise TypeError(f"runner is not callable: {specification}")
    return runner


def refresh_ledger(preset: Preset) -> dict[str, Any]:
    result = load_runner(preset.runner)()
    if not isinstance(result, dict) or "passed" not in result:
        raise ValueError(f"runner returned an invalid result for {preset.name}")
    return result


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def semantically_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return canonical_json(left) == canonical_json(right)


def build_panel(preset: Preset, ledger: Mapping[str, Any]) -> Panel:
    acceptance = ledger.get("acceptance", {})
    if not isinstance(acceptance, Mapping):
        acceptance = {}
    values: list[tuple[str, float | int | bool]] = []
    for metric in preset.metrics:
        value = resolve_path(ledger, metric.path)
        if not isinstance(value, (int, float, bool)):
            raise TypeError(f"metric {metric.path!r} is not scalar")
        values.append((metric.label, value))
    return Panel(
        preset=preset.name,
        title=preset.title,
        sector=preset.sector,
        task=preset.task,
        passed=bool(ledger["passed"]),
        acceptance_passed=sum(bool(value) for value in acceptance.values()),
        acceptance_total=len(acceptance),
        metrics=tuple(values),
        establishes=preset.establishes,
        does_not_establish=preset.does_not_establish,
    )


def build_panels(
    names: Iterable[str] | None = None,
    *,
    refresh: bool = False,
    data_root: Path | None = None,
    presets: Sequence[Preset] | None = None,
) -> tuple[Panel, ...]:
    selected = select_presets(names, presets)
    panels: list[Panel] = []
    for preset in selected:
        ledger = refresh_ledger(preset) if refresh else load_ledger(preset, data_root)
        panels.append(build_panel(preset, ledger))
    return tuple(panels)


def export_bundle(
    panels: Sequence[Panel],
    output_directory: str | Path,
    *,
    render: bool = True,
) -> dict[str, Any]:
    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "openwave.m9.instrumentation-export.v1",
        "panels": [panel.to_dict() for panel in panels],
    }
    json_path = destination / "m9_instrumentation.json"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    images: list[str] = []
    if render:
        from .renderer import render_panel

        for panel in panels:
            image_path = destination / f"{panel.preset}.png"
            render_panel(panel, image_path)
            images.append(str(image_path))
    return {
        "json": str(json_path),
        "images": images,
        "panel_count": len(panels),
    }


def run_instrumentation_study(
    *,
    data_root: Path | None = None,
    preset_path: Path | None = None,
) -> dict[str, Any]:
    presets = load_presets(preset_path)
    panels = build_panels(data_root=data_root, presets=presets)
    names = [preset.name for preset in presets]
    required = {"scalar-observables", "radial-dynamics", "transverse-radiation"}
    forbidden = ("electron preset", "positron preset", "standard model preset")
    serialized = " ".join(names).lower()
    acceptance = {
        "validated_core_registered": required.issubset(set(names)),
        "all_ledgers_pass": all(panel.passed for panel in panels),
        "all_acceptance_panels_nonempty": all(
            panel.acceptance_total > 0 for panel in panels
        ),
        "claim_boundaries_present": all(
            panel.establishes and panel.does_not_establish for panel in panels
        ),
        "no_particle_identity_default": not any(
            item in serialized for item in forbidden
        ),
        "metric_paths_resolve": all(panel.metrics for panel in panels),
    }
    return {
        "schema": "openwave.m9.instrumentation-result.v1",
        "task": "M9.8",
        "presets": names,
        "panels": [panel.to_dict() for panel in panels],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
