from __future__ import annotations

import json
from pathlib import Path

from openwave.xperiments.m9_cat_ept._launcher import main
from openwave.xperiments.m9_cat_ept.instrumentation import (
    build_panels,
    export_bundle,
    load_presets,
    resolve_path,
    run_instrumentation_study,
    select_presets,
    semantically_equal,
)


def _write_ledgers(root: Path) -> None:
    scalar = {
        "passed": True,
        "acceptance": {"a": True},
        "maximum_errors": {"norm_relative": 1e-12, "energy_relative": 2e-12},
        "reference_member": {"rms_radius": 0.9, "phase_frequency": 0.5},
    }
    radial = {
        "passed": True,
        "acceptance": {"a": True, "b": True},
        "long_time_run": {
            "phase_metrics": {"fidelity": 0.999},
            "max_norm_drift": 1e-14,
            "max_total_energy_relative_drift": 1e-8,
            "max_gauss_residual_relative": 1e-13,
            "final": {"core_fraction_r16": 0.99},
        },
    }
    transverse = {
        "passed": True,
        "acceptance": {"a": True},
        "long_run": {
            "emitted_energy": 1e-3,
            "absorbed_energy": 8e-4,
            "corrected_energy_relative_drift": 2e-6,
            "max_charge_density": 0.0,
            "final": {"field_energy_central_fraction": 0.6},
        },
    }
    transported = {
        "passed": True,
        "acceptance": {"a": True, "b": True},
        "refinement": {"observed_order": 1.9},
        "long_run": {
            "max_norm_drift": 1e-9,
            "max_corrected_energy_relative_drift": 1e-6,
            "emitted_energy": 2e-5,
            "final": {"gauss_residual_relative": 0.02},
        },
        "transport": {"final_separation": -2.0},
    }
    values = {
        "m9_5_soliton_observable_result.json": scalar,
        "m9_7b3_dirac_electrostatic_dynamics_result.json": radial,
        "m9_7c_transverse_maxwell_spinor_result.json": transverse,
        "m9_9_transported_maxwell_dirac_result.json": transported,
    }
    for name, payload in values.items():
        (root / name).write_text(json.dumps(payload), encoding="utf-8")


def test_manifest_defines_validated_non_particle_presets() -> None:
    presets = load_presets()
    names = {preset.name for preset in presets}
    assert {
        "scalar-observables",
        "radial-dynamics",
        "transverse-radiation",
        "transported-maxwell-dirac",
    }.issubset(names)
    assert all(preset.does_not_establish for preset in presets)
    assert all("electron" not in preset.name for preset in presets)


def test_path_resolution_supports_mappings_and_sequences() -> None:
    payload = {"a": {"b": [{"c": 3.0}]}}
    assert resolve_path(payload, "a.b.0.c") == 3.0


def test_build_panels_from_ledgers(tmp_path: Path) -> None:
    _write_ledgers(tmp_path)
    panels = build_panels(data_root=tmp_path)
    assert len(panels) == 4
    assert all(panel.passed for panel in panels)
    assert all(panel.acceptance_passed == panel.acceptance_total for panel in panels)


def test_selection_rejects_unknown_preset() -> None:
    try:
        select_presets(["electron"])
    except KeyError as error:
        assert "unknown preset" in str(error)
    else:
        raise AssertionError("unknown preset should fail")


def test_export_writes_json_and_png(tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledgers"
    ledger_root.mkdir()
    _write_ledgers(ledger_root)
    panels = build_panels(data_root=ledger_root)
    result = export_bundle(panels, tmp_path / "export")
    assert Path(result["json"]).is_file()
    assert len(result["images"]) == 4
    assert all(Path(path).is_file() for path in result["images"])


def test_semantic_comparison_ignores_key_order() -> None:
    assert semantically_equal({"b": 2, "a": 1}, {"a": 1, "b": 2})


def test_study_passes_with_fixture_ledgers(tmp_path: Path) -> None:
    _write_ledgers(tmp_path)
    result = run_instrumentation_study(data_root=tmp_path)
    assert result["passed"]
    assert all(result["acceptance"].values())


def test_launcher_lists_presets(capsys) -> None:
    assert main(["--list"]) == 0
    output = capsys.readouterr().out
    assert "scalar-observables" in output
    assert "transverse-radiation" in output
    assert "transported-maxwell-dirac" in output
