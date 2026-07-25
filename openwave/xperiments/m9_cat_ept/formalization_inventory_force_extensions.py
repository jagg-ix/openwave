"""Additional current-tree formal witnesses required by M9.96 source/force closure."""
from __future__ import annotations

FORCE_EXTENSION_LEAN_SOURCES = (
    (
        "anomalous-moment-maxwell-links",
        "Physlib/QuantumMechanics/ComplexAction/FirstQuantizedQED/AnomalousMomentLinks.lean",
        "51c0e5d9adacf144b6c902ff47d0850071083a0c",
        (
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks",
        ),
        "kernel_checked_structural",
    ),
    (
        "maxwell-continuity-covariant",
        "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/MaxwellContinuityCovariant.lean",
        "553c9c77b895cfcb1681b594dc370a82675412b1",
        (
            "Physlib.QuantumMechanics.ComplexAction.Electromagnetic.MaxwellContinuityCovariant",
        ),
        "kernel_checked_with_conditional_green_interface",
    ),
)

FORCE_EXTENSION_DECLARATIONS = {
    "magnetic_moment_spin": {
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.spinTensor_12_eq_spinProjectorOp",
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.pauliCoupling_gauge_invariant",
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.magneticInteraction_dirac",
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.magneticInteraction_gFactor",
        ),
        "boundary": (
            "the Pauli-Maxwell coupling is gauge invariant but the loop anomaly is not derived from the candidate",
        ),
    },
    "electric_force": {
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.Electromagnetic.MaxwellContinuityCovariant.fourCurrent_conserved",
            "Physlib.QuantumMechanics.ComplexAction.Electromagnetic.MaxwellContinuityCovariant.heras_existence_theorem",
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations.maxwellStressEnergy_faraday_gauge_invariant",
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations.electromagneticStationary_iff_sourceFree",
        ),
        "boundary": (
            "the retarded-current construction remains conditional on Green inversion",
            "the M9.96 force triangle is static and does not establish center acceleration from the full PDE",
        ),
    },
    "magnetic_force": {
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.pauliCoupling_gauge_invariant",
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.magneticInteraction_dirac",
            "Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMomentLinks.magneticInteraction_gFactor",
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations.maxwellStressEnergy_faraday_gauge_invariant",
        ),
        "boundary": (
            "the static Maxwell-stress result is not a dynamical spinor-Maxwell stationary-pair theorem",
        ),
    },
}
