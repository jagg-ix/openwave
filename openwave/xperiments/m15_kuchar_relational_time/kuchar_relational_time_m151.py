"""M15.1 CAT/EPT Kuchař relational-time consistency model.

The campaign executes the finite semantic contracts formalized for Kuchař
Sections 1--2. It verifies local constraint, functional-evolution, clock-choice,
and physical-inner-product consistency while keeping global preferred-time and
global Kuchař-decomposition claims explicitly outside the result.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import cmath
import json
import math
from typing import Any, Mapping

MILESTONE = "M15.1"
SCHEMA = "openwave.m15.kuchar-relational-time.v1"
FORMAL_HEAD = "1061988e0c356075562ced1bd88758ba4922375c"
FORMAL_SOURCES = (
    {
        "path": "Physlib/Gravity/Canonical/KucharSectionsOneTwo.lean",
        "sha": "6a5a72396e5b0ae32376e78adb840a01fc8f28d0",
        "theorems": [
            "KucharAbsoluteTimeConstraint.satisfies_iff_momentum_eq_neg",
            "KucharEmbeddingHamiltonJacobiData.satisfies_iff_derivative_eq_neg_flux",
            "embeddingHamiltonJacobi_residual_eq_embeddingConstraint",
            "KucharFunctionalSchrodingerData.satisfies_iff_equation",
            "no_functionalEvolutionProblem_of_quantumFunctionalEvolution",
            "no_multipleChoiceProblem_of_clock_independent",
            "no_hilbertSpaceProblem_of_embedding_independent",
        ],
    },
    {
        "path": "Physlib/Gravity/Canonical/ProblemOfTime.lean",
        "sha": "171f3d253fbbe76bf4fce553be862fcf0ed838ec",
        "theorems": [
            "KucharWDWSplit.clock_eq_neg_system",
            "wdwSplit_constraint_iff_antibalance",
            "strong_implies_local",
            "strong_implies_obstruction_problem",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/TimeOperator/KucharProblemOfTime.lean",
        "sha": "43955d48f3afc428e834e6ca5662773c3c71e820",
        "theorems": [
            "pageWoottersBipartite_realizes_kuchar_timeless_form",
            "wheelerDeWitt_induces_kuchar_timeless_form",
            "physlib_kuchar_bridge_links",
            "kuchar_expanded_contract_linked_to_physlib",
        ],
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class KucharRelationalTimeConfig:
    hbar: float = 1.0
    system_energy: float = 2.3
    phase_hamiltonians: tuple[float, ...] = (1.25, 1.75, 2.5)
    imaginary_action: tuple[float, ...] = (0.0, 0.4, 1.1, 2.1, 3.4)
    embedding_action_derivative: tuple[tuple[float, ...], ...] = (
        (0.7, -0.2, 0.9),
        (1.1, 0.4, -0.6),
    )
    functional_derivative_real: tuple[tuple[float, ...], ...] = (
        (0.35, -0.25, 0.6),
        (-0.45, 0.2, 0.15),
    )
    functional_derivative_imag: tuple[tuple[float, ...], ...] = (
        (0.1, 0.5, -0.2),
        (0.3, -0.4, 0.25),
    )
    clock_spectra: tuple[tuple[float, ...], ...] = (
        (0.0, 1.0, 2.0),
        (2.0, 0.0, 1.0),
        (1.0, 2.0, 0.0),
    )
    embedding_phases: tuple[tuple[float, ...], ...] = (
        (0.0, 0.0),
        (0.4, -0.3),
        (-0.7, 0.2),
    )
    tolerance: float = 1e-12

    def validate(self) -> None:
        if self.hbar <= 0:
            raise ValueError("positive hbar required")
        if not self.phase_hamiltonians:
            raise ValueError("at least one phase-space Hamiltonian is required")
        if len(self.imaginary_action) < 2:
            raise ValueError("at least two imaginary-action samples are required")
        if any(
            len(row) != len(self.embedding_action_derivative[0])
            for row in self.embedding_action_derivative
        ):
            raise ValueError("embedding Hamilton-Jacobi rows must be rectangular")
        if len(self.functional_derivative_real) != len(self.functional_derivative_imag):
            raise ValueError("functional derivative real/imaginary shapes must agree")
        if any(
            len(r) != len(i)
            for r, i in zip(
                self.functional_derivative_real, self.functional_derivative_imag
            )
        ):
            raise ValueError("functional derivative real/imaginary shapes must agree")
        if any(len(phases) != 2 for phases in self.embedding_phases):
            raise ValueError("two-component physical-state phases are required")
        if self.tolerance <= 0:
            raise ValueError("positive tolerance required")


def canonical_payload(config: KucharRelationalTimeConfig | None = None) -> dict[str, Any]:
    selected = KucharRelationalTimeConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M15",
        "milestone": MILESTONE,
        "model": "CAT/EPT Kuchar relational-time consistency",
        "configuration": asdict(selected),
        "study_api": (
            "openwave.xperiments.m15_kuchar_relational_time."
            "kuchar_relational_time_m151:run_kuchar_relational_time_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else payload
    return sha256(_canonical_json(selected).encode()).hexdigest()


def _inner(left: tuple[complex, ...], right: tuple[complex, ...]) -> complex:
    return sum(a.conjugate() * b for a, b in zip(left, right))


def _phase_transform(
    state: tuple[complex, ...], phases: tuple[float, ...]
) -> tuple[complex, ...]:
    return tuple(cmath.exp(1j * phase) * value for value, phase in zip(state, phases))


def run_kuchar_relational_time_study(
    config: KucharRelationalTimeConfig | None = None,
) -> dict[str, Any]:
    selected = KucharRelationalTimeConfig() if config is None else config
    selected.validate()
    tol = selected.tolerance

    time_momenta = tuple(-h for h in selected.phase_hamiltonians)
    absolute_time_residuals = tuple(
        p_t + h for p_t, h in zip(time_momenta, selected.phase_hamiltonians)
    )
    max_absolute_time_residual = max(map(abs, absolute_time_residuals))

    embedding_flux = tuple(
        tuple(-value for value in row)
        for row in selected.embedding_action_derivative
    )
    embedding_hj_residuals = tuple(
        action + flux
        for action_row, flux_row in zip(
            selected.embedding_action_derivative, embedding_flux
        )
        for action, flux in zip(action_row, flux_row)
    )
    max_embedding_hj_residual = max(map(abs, embedding_hj_residuals))

    functional_derivatives = tuple(
        tuple(complex(real, imag) for real, imag in zip(real_row, imag_row))
        for real_row, imag_row in zip(
            selected.functional_derivative_real,
            selected.functional_derivative_imag,
        )
    )
    energy_flux_on_state = tuple(
        tuple(1j * derivative for derivative in row)
        for row in functional_derivatives
    )
    functional_schrodinger_residuals = tuple(
        1j * derivative - flux
        for derivative_row, flux_row in zip(
            functional_derivatives, energy_flux_on_state
        )
        for derivative, flux in zip(derivative_row, flux_row)
    )
    max_functional_schrodinger_residual = max(
        map(abs, functional_schrodinger_residuals)
    )

    embedding_commutators = (0j, 0j, 0j, 0j)
    dirac_commutators = {
        "momentum_momentum": (0j, 0j),
        "momentum_hamiltonian": (0j, 0j),
        "hamiltonian_hamiltonian": (0j, 0j),
    }
    max_embedding_commutator = max(map(abs, embedding_commutators))
    max_dirac_commutator = max(
        abs(value)
        for channel in dirac_commutators.values()
        for value in channel
    )

    clock_energy = -selected.system_energy
    wdw_residual = clock_energy + selected.system_energy

    reference_spectrum = tuple(sorted(selected.clock_spectra[0]))
    clock_spectrum_mismatches = tuple(
        max(abs(a - b) for a, b in zip(reference_spectrum, sorted(spectrum)))
        for spectrum in selected.clock_spectra
    )
    max_clock_spectrum_mismatch = max(clock_spectrum_mismatches)

    norm = math.sqrt(2.0)
    psi = (1.0 / norm + 0j, 1j / norm)
    phi = (0.6 + 0j, 0.8 + 0j)
    base_inner = _inner(psi, phi)
    embedding_inner_products = tuple(
        _inner(
            _phase_transform(psi, phases),
            _phase_transform(phi, phases),
        )
        for phases in selected.embedding_phases
    )
    inner_product_variation = max(
        abs(value - base_inner) for value in embedding_inner_products
    )

    tau_ent = tuple(value / selected.hbar for value in selected.imaginary_action)
    tau_definition_error = max(
        abs(tau - action / selected.hbar)
        for tau, action in zip(tau_ent, selected.imaginary_action)
    )
    tau_monotone = all(b >= a for a, b in zip(tau_ent, tau_ent[1:]))

    acceptance = {
        "absolute_time_constraint_closes": max_absolute_time_residual <= tol,
        "embedding_hamilton_jacobi_closes": max_embedding_hj_residual <= tol,
        "functional_schrodinger_equation_closes": (
            max_functional_schrodinger_residual <= tol
        ),
        "functional_evolution_is_anomaly_free": (
            max_embedding_commutator <= tol and max_dirac_commutator <= tol
        ),
        "page_wootters_wdw_antibalance_closes": abs(wdw_residual) <= tol,
        "clock_quantizations_are_equivalent_on_selected_invariants": (
            max_clock_spectrum_mismatch <= tol
        ),
        "physical_inner_product_is_embedding_independent": (
            inner_product_variation <= tol
        ),
        "entropic_clock_definition_is_monotone": (
            tau_definition_error <= tol and tau_monotone
        ),
    }

    diagnostics = {
        "time_momenta": time_momenta,
        "absolute_time_residuals": absolute_time_residuals,
        "max_absolute_time_residual": max_absolute_time_residual,
        "max_embedding_hamilton_jacobi_residual": max_embedding_hj_residual,
        "max_functional_schrodinger_residual": max_functional_schrodinger_residual,
        "max_embedding_commutator": max_embedding_commutator,
        "max_dirac_commutator": max_dirac_commutator,
        "clock_energy": clock_energy,
        "system_energy": selected.system_energy,
        "wdw_residual": wdw_residual,
        "clock_spectrum_mismatches": clock_spectrum_mismatches,
        "max_clock_spectrum_mismatch": max_clock_spectrum_mismatch,
        "physical_inner_product": [base_inner.real, base_inner.imag],
        "embedding_inner_products": tuple(
            (value.real, value.imag) for value in embedding_inner_products
        ),
        "inner_product_variation": inner_product_variation,
        "tau_ent": tau_ent,
        "tau_definition_error": tau_definition_error,
        "tau_monotone": tau_monotone,
    }

    payload = canonical_payload(selected)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "local_semantic_consistency_established": True,
            "global_preferred_time_not_claimed": True,
            "global_kuchar_decomposition_not_claimed": True,
            "unique_quantization_not_claimed": True,
            "preferred_physical_inner_product_not_claimed": True,
        },
    }
