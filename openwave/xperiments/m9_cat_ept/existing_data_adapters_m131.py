"""M9.131b: dataset adapter contracts for relational and relaxation carriers."""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def adapt_moreva_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    adapted = []
    for row in rows:
        adapted.append({
            "observation_id": str(row["observation_id"]),
            "dataset_id": str(row["dataset_id"]),
            "domain": "relational-conditioning",
            "x": float(row["clock_index"]),
            "y": float(row["conditional_fidelity"]),
            "uncertainty": float(row["uncertainty"]),
            "units": {"x": "clock-index", "y": "fidelity"},
            "split": str(row["split"]),
        })
    return tuple(adapted)


def adapt_relaxation_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    adapted = []
    for row in rows:
        adapted.append({
            "observation_id": str(row["observation_id"]),
            "dataset_id": str(row["dataset_id"]),
            "domain": "binary-relaxation",
            "x": float(row["time_s"]),
            "y": float(row["occupation"]),
            "uncertainty": float(row["uncertainty"]),
            "units": {"x": "s", "y": "occupation"},
            "split": str(row["split"]),
        })
    return tuple(adapted)


def run_dataset_adapters() -> dict[str, Any]:
    moreva = adapt_moreva_rows((
        {"observation_id":"m0","dataset_id":"moreva-2014-page-wootters","clock_index":0,"conditional_fidelity":0.99,"uncertainty":0.01,"split":"holdout"},
    ))
    relaxation = adapt_relaxation_rows((
        {"observation_id":"q0","dataset_id":"lu-2003-quantum-dot","time_s":0.0,"occupation":0.82,"uncertainty":0.02,"split":"calibration"},
        {"observation_id":"q1","dataset_id":"lu-2003-quantum-dot","time_s":0.2,"occupation":0.55,"uncertainty":0.02,"split":"holdout"},
    ))
    rows = moreva + relaxation
    acceptance = {
        "relational_adapter_preserves_domain": moreva[0]["domain"] == "relational-conditioning",
        "relaxation_adapter_preserves_units": relaxation[0]["units"]["x"] == "s",
        "split_labels_are_preserved": {row["split"] for row in rows} == {"calibration", "holdout"},
        "adapters_emit_normalizer_schema": all(set(("observation_id","dataset_id","domain","x","y","uncertainty","units","split")).issubset(row) for row in rows),
    }
    return {"schema":"openwave.m9.existing-data-adapters.v1","task":"M9.131b","rows":rows,"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"adapter_contracts_ready":True,"real_rows_imported":False}}
