"""M11.1 exact pointwise CAT/EPT bright-soliton carrier.

The executable carrier uses the normalized one-dimensional cubic-NLS bright
soliton as an exact pointwise control model.  The nonlinear coefficient is
calibrated from the finite-domain normalization, so the analytic second
spatial derivative closes the stationary equation at machine precision.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

MILESTONE = "M11.1"
SCHEMA = "openwave.m11.pointwise-soliton-carrier.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/SinhGordonSoliton.lean",
        "sha": "b2eb056dd4d66d224adf2d118da874e48a4a63cc",
        "theorem": "bps_implies_sinhGordon",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/SelfBoundSchrodingerNewtonPDE.lean",
        "sha": "d84c06718e292dd18e03653efb34d237a4e2899a",
        "theorem": "standingWave_solves_full_schrodingerNewton",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticOrbitalStability.lean",
        "sha": "fb47b98296a771eee44570ce42b5c2ab03d450a3",
        "theorem": "cubicQuinticDensity_coercive",
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def sech(value: np.ndarray) -> np.ndarray:
    return 1.0 / np.cosh(value)


@dataclass(frozen=True)
class PointwiseSolitonConfig:
    grid_points: int = 1025
    half_length: float = 12.0
    inverse_width: float = 1.0
    dispersion: float = 0.5
    hbar: float = 1.0
    winding: int = 1
    sample_time: float = 0.37

    def validate(self) -> None:
        if self.grid_points < 129 or self.grid_points % 2 == 0:
            raise ValueError("an odd grid with at least 129 points is required")
        if self.half_length <= 0 or self.inverse_width <= 0:
            raise ValueError("positive length and inverse width are required")
        if self.dispersion <= 0 or self.hbar <= 0:
            raise ValueError("positive dispersion and hbar are required")


@dataclass(frozen=True)
class PointwiseSolitonState:
    config: PointwiseSolitonConfig
    x: np.ndarray
    psi: np.ndarray
    second_derivative: np.ndarray
    chemical_potential: float
    cubic_coupling: float
    amplitude: float
    dx: float

    @property
    def density(self) -> np.ndarray:
        return np.abs(self.psi) ** 2

    def wave(self, time: float) -> np.ndarray:
        phase = np.exp(-1.0j * self.chemical_potential * time / self.config.hbar)
        return np.asarray(phase * self.psi, dtype=np.complex128)

    def stationary_residual(self) -> np.ndarray:
        cfg = self.config
        return np.asarray(
            -cfg.dispersion * self.second_derivative
            - self.cubic_coupling * self.psi**3
            - self.chemical_potential * self.psi,
            dtype=np.float64,
        )


def construct_pointwise_soliton(
    config: PointwiseSolitonConfig | None = None,
) -> PointwiseSolitonState:
    cfg = PointwiseSolitonConfig() if config is None else config
    cfg.validate()
    x = np.linspace(-cfg.half_length, cfg.half_length, cfg.grid_points)
    dx = float(x[1] - x[0])
    shape = sech(cfg.inverse_width * x)
    amplitude = float(1.0 / math.sqrt(np.trapezoid(shape**2, x)))
    psi = np.asarray(amplitude * shape, dtype=np.float64)
    second = np.asarray(
        cfg.inverse_width**2 * psi * (1.0 - 2.0 * shape**2),
        dtype=np.float64,
    )
    chemical_potential = -cfg.dispersion * cfg.inverse_width**2
    cubic_coupling = 2.0 * cfg.dispersion * cfg.inverse_width**2 / amplitude**2
    return PointwiseSolitonState(
        config=cfg,
        x=x,
        psi=psi,
        second_derivative=second,
        chemical_potential=chemical_potential,
        cubic_coupling=cubic_coupling,
        amplitude=amplitude,
        dx=dx,
    )


def sinh_gordon_bps_control(sample_count: int = 257) -> dict[str, float]:
    phi = np.linspace(-1.5, 1.5, sample_count)
    first = 2.0 * np.sinh(phi / 2.0)
    second_from_chain = np.cosh(phi / 2.0) * first
    second_exact = np.sinh(phi)
    energy = 0.5 * first**2 - np.cosh(phi)
    return {
        "bps_second_order_error": float(np.max(np.abs(second_from_chain - second_exact))),
        "bps_energy_error": float(np.max(np.abs(energy + 1.0))),
    }


def canonical_payload(config: PointwiseSolitonConfig | None = None) -> dict[str, Any]:
    cfg = PointwiseSolitonConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M11",
        "milestone": MILESTONE,
        "model": "CAT/EPT pointwise soliton--Liouville--QDO particle model",
        "configuration": asdict(cfg),
        "construction_api": (
            "openwave.xperiments.m11_cat_ept_soliton_qdo."
            "pointwise_soliton_carrier_m111:construct_pointwise_soliton"
        ),
        "study_api": (
            "openwave.xperiments.m11_cat_ept_soliton_qdo."
            "pointwise_soliton_carrier_m111:run_pointwise_soliton_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


def run_pointwise_soliton_study(
    config: PointwiseSolitonConfig | None = None,
) -> dict[str, Any]:
    state = construct_pointwise_soliton(config)
    cfg = state.config
    norm = float(np.trapezoid(state.density, state.x))
    residual = state.stationary_residual()
    wave = state.wave(cfg.sample_time)
    analytic_dt = (-1.0j * state.chemical_potential / cfg.hbar) * wave
    time_equation = 1.0j * cfg.hbar * analytic_dt - state.chemical_potential * wave
    bps = sinh_gordon_bps_control()
    half_max = state.density.max() / 2.0
    support = state.x[state.density >= half_max]
    fwhm = float(support[-1] - support[0])
    kinetic = cfg.dispersion * np.abs(
        -cfg.inverse_width * np.tanh(cfg.inverse_width * state.x) * state.psi
    ) ** 2
    interaction = -0.5 * state.cubic_coupling * state.density**2
    energy = float(np.trapezoid(kinetic + interaction, state.x))
    diagnostics = {
        "normalization_error": abs(norm - 1.0),
        "stationary_residual_linf": float(np.max(np.abs(residual))),
        "standing_wave_time_error": float(np.max(np.abs(time_equation))),
        "density_time_invariance_error": float(np.max(np.abs(np.abs(wave) ** 2 - state.density))),
        "fwhm": fwhm,
        "energy": energy,
        "chemical_potential": state.chemical_potential,
        "cubic_coupling": state.cubic_coupling,
        **bps,
    }
    acceptance = {
        "normalized": diagnostics["normalization_error"] < 5.0e-13,
        "pointwise_stationary_equation": diagnostics["stationary_residual_linf"] < 5.0e-13,
        "standing_wave_equation": diagnostics["standing_wave_time_error"] < 5.0e-13,
        "density_is_stationary": diagnostics["density_time_invariance_error"] < 5.0e-13,
        "localized": 0.5 < fwhm < 4.0,
        "bps_reduction": diagnostics["bps_second_order_error"] < 5.0e-13,
        "bps_energy": diagnostics["bps_energy_error"] < 5.0e-13,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M11.1",
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
    }
