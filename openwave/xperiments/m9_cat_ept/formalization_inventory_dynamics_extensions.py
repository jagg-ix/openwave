"""M9.97 formal witnesses for particle dynamics and spin precession."""
from __future__ import annotations


def _names(value: str) -> tuple[str, ...]:
    return tuple(value.split())


DYNAMICS_EXTENSION_LEAN_SOURCES = (
    (
        "thomas-bmt-magic-cancellation",
        "Physlib/QuantumMechanics/ComplexAction/MuonAnomaly/ThomasBMTMagicCancellation.lean",
        "7a7863819b8c86dfa1eb5a9647b4f59250885d4f",
        (
            "Physlib.QuantumMechanics.ComplexAction.MuonAnomaly.ThomasBMTMagicCancellation",
        ),
        "kernel_checked_with_covariant_boundary",
    ),
    (
        "em-particle-dynamics",
        "Physlib/QuantumMechanics/ComplexAction/ParametrizedTetradGravity/EMParticleDynamics.lean",
        "a1ef5ce20dfe0b843b124c6fa7a85b6809b8df50",
        (
            "Physlib.QuantumMechanics.ComplexAction.ParametrizedTetradGravity.EMParticleDynamics",
        ),
        "kernel_checked_algebraic_dynamics_surface",
    ),
    (
        "distributional-point-particle-three-d",
        "Physlib/Electromagnetism/PointParticle/ThreeDimension.lean",
        "ac69848c2707b128a24afa4e2cb3e228b1ba4859",
        ("Electromagnetism.DistElectromagneticPotential",),
        "kernel_checked_distributional_source",
    ),
)


DYNAMICS_EXTENSION_DECLARATIONS = {
    "magnetic_moment_spin": {
        "declarations": _names(
            """
            Physlib.QuantumMechanics.ComplexAction.MuonAnomaly.ThomasBMTMagicCancellation.heisenberg_precession_of_dipole
            Physlib.QuantumMechanics.ComplexAction.MuonAnomaly.ThomasBMTMagicCancellation.tbmtSpinRate_rest_eq_diracPauli
            Physlib.QuantumMechanics.ComplexAction.MuonAnomaly.ThomasBMTMagicCancellation.qed_forceLaw_chain
            """
        ),
        "boundary": (
            "the rest-frame Dirac-Pauli precession is proved, but the covariant boost and Thomas splitting remain outside the witness",
            "the Schwinger value is imported; the loop computation of F2 is not formalized",
        ),
    },
    "electric_force": {
        "declarations": _names(
            """
            Physlib.QuantumMechanics.ComplexAction.ParametrizedTetradGravity.EMParticleDynamics.coulombPotential_eq
            Physlib.QuantumMechanics.ComplexAction.ParametrizedTetradGravity.EMParticleDynamics.coulomb_symm
            Electromagnetism.DistElectromagneticPotential.threeDimPointParticle_electricField
            Electromagnetism.DistElectromagneticPotential.threeDimPointParticle_div_electricField
            """
        ),
        "boundary": (
            "the exact point-source and Coulomb carriers do not identify a finite winding packet with a physical point charge",
            "full center acceleration of the extended winding state remains a numerical obligation",
        ),
    },
    "magnetic_force": {
        "declarations": _names(
            """
            Physlib.QuantumMechanics.ComplexAction.MuonAnomaly.ThomasBMTMagicCancellation.heisenberg_precession_of_dipole
            Physlib.QuantumMechanics.ComplexAction.MuonAnomaly.ThomasBMTMagicCancellation.tbmtSpinRate_rest_eq_diracPauli
            Physlib.QuantumMechanics.ComplexAction.ParametrizedTetradGravity.EMParticleDynamics.helmholtz_decomp
            Physlib.QuantumMechanics.ComplexAction.ParametrizedTetradGravity.EMParticleDynamics.longitudinal_killed
            """
        ),
        "boundary": (
            "the rest-frame Pauli torque need not equal the response of a relativistic winding packet",
            "the full vector T-BMT and Frenet-Serret dynamics remain outside the imported theorem",
        ),
    },
}
