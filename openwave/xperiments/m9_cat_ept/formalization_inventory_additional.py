"""Additional ZIL graphs discovered by repository-wide formalization search."""
from __future__ import annotations


def _names(value: str) -> tuple[str, ...]:
    return tuple(value.split())


ADDITIONAL_ZIL_GRAPHS = (
    {
        "id": "cauchy-weak-limit",
        "module": "physlib.quantum.open_systems.cauchy_weak_limit",
        "source_path": "formalization/zil/cauchy-weak-limit.zc",
        "source_blob": "9bf413de689d0f7715096492e4fdfcb1e4985cdd",
        "entities": {
            "component": _names("""
                cauchy_probability_measure convergence_in_distribution
                ae_tendsto_distribution probability_measure_topology
            """),
            "source": _names("""
                schwarz2016_eq33_eq34 schwarz2016_eq42
                schwarz2016_continuum_limit
            """),
            "claim": _names("""
                standard_cauchy_reference_space affine_cauchy_sample_ae_limit
                cauchy_broadening_distribution_limit
                cauchy_broadening_law_tendsto_dirac
            """),
            "proof": _names("""
                QuantumMechanics.LindbladDrivenLeads.affineCauchySample_ae_tendsto
                QuantumMechanics.LindbladDrivenLeads.affineCauchySample_tendstoInDistribution
                QuantumMechanics.LindbladDrivenLeads.affineCauchyLaw_tendsto_dirac
            """),
        },
        "rules": _names("verified_claim pending_claim"),
        "queries": _names("""
            claim_statuses proof_registry dependency_edges reused_components
            source_traceability
        """),
        "open_targets": (),
        "witness_prefixes": (
            "ProbabilityTheory.",
            "MeasureTheory.",
            "ProbabilityMeasure",
            "QuantumMechanics.LindbladDrivenLeads",
        ),
    },
    {
        "id": "lindblad-trace-preservation",
        "module": "physlib.quantum.open_systems.lindblad_trace_preservation",
        "source_path": "formalization/zil/lindblad-trace-preservation.zc",
        "source_blob": "1ab159b05e27747e9cd9564d0b38eb5b7e9b6864",
        "entities": {
            "component": _names("""
                linear_map_trace trace_mul_comm trace_mul_cycle
                hilbert_schmidt_linear_equiv
            """),
            "source": _names("schwarz2016_eq36 schwarz2016_eq40"),
            "claim": _names("""
                hilbert_schmidt_trace_functional
                hamiltonian_part_trace_zero gksl_dissipator_trace_zero
                lddl_generator_trace_zero
            """),
            "proof": _names("""
                QuantumMechanics.LindbladDrivenLeads.hsTrace_hamiltonianPartHS
                QuantumMechanics.LindbladDrivenLeads.hsTrace_lindbladDissipatorHS
                QuantumMechanics.LindbladDrivenLeads.hsTrace_lddlGeneratorHS
                QuantumMechanics.LindbladDrivenLeads.hsTrace_comp_lddlGeneratorHS
            """),
        },
        "rules": _names("verified_claim pending_claim"),
        "queries": _names("""
            claim_statuses proof_registry dependency_edges reused_components
            source_traceability
        """),
        "open_targets": (),
        "witness_prefixes": (
            "LinearMap.",
            "HilbertSchmidtOperatorSpace.",
            "QuantumMechanics.LindbladDrivenLeads",
        ),
    },
)
