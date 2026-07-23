"""Public M9.16 facade with canonical JSON boolean normalization."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from . import lindblad_information_loss as _implementation

LindbladParameters = _implementation.LindbladParameters
exact_density = _implementation.exact_density
initial_density = _implementation.initial_density
zero_loss_study = _implementation.zero_loss_study


def run_lindblad_information_study() -> dict[str, Any]:
    result = deepcopy(_implementation.run_lindblad_information_study())
    key = "zero_loss_reduces_to_unitary"
    result["acceptance"][key] = bool(result["acceptance"][key])
    result["passed"] = bool(result["passed"])
    return result


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
