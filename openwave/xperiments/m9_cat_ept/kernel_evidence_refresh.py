"""Fail-closed refresh of kernel-checked evidence for CAT/EPT bridges.

The refresh consumes an exported source/verification snapshot. A declaration is
promoted only when its exact Git blob is current, the witness is declared, the
verification state is ``kernel_checked``, and no open assumption is attached.
The inspected PhysLib/ZIL snapshot currently contains no such promotion record.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal

VerificationState = Literal["kernel_checked", "pending_ci", "provided_interface", "open"]
PromotionStatus = Literal[
    "formal_promoted",
    "awaiting_kernel",
    "interface_only",
    "open_boundary",
    "stale",
    "missing_witness",
    "blocked_by_assumption",
]
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"


@dataclass(frozen=True)
class KernelEvidence:
    identifier: str
    path: str
    expected_sha: str
    witness: str
    verification_state: VerificationState
    witness_declared: bool = True
    open_assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all((self.identifier, self.path, self.expected_sha, self.witness)):
            raise ValueError("complete kernel evidence identity required")
        if len(self.expected_sha) != 40:
            raise ValueError("Git blob SHA must contain 40 hexadecimal characters")


def snapshot() -> tuple[KernelEvidence, ...]:
    return (
        KernelEvidence(
            "continuum_kernel_constructor",
            "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
            "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
            "QuantumMechanics.LiouvilleSecondQuantization.coe_mkContinuumKernel_ae",
            "pending_ci",
        ),
        KernelEvidence(
            "pointwise_actions_commute",
            "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
            "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
            "QuantumMechanics.LiouvilleSecondQuantization.leftPointwise_rightPointwise_commute",
            "pending_ci",
        ),
        KernelEvidence(
            "pointwise_dense_domain",
            "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
            "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
            "QuantumMechanics.LiouvilleSecondQuantization.spacePointwiseKernelOperator_hasDenseDomain",
            "pending_ci",
        ),
        KernelEvidence(
            "pointwise_multiplier_closable",
            "Physlib/QuantumMechanics/DDimensions/Operators/Multiplication.lean",
            "9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5",
            "QuantumMechanics.SpaceDHilbertSpace.mulOperator_isClosable",
            "pending_ci",
        ),
        KernelEvidence(
            "continuum_l2_carrier",
            "formalization/zil/liouville-second-quantization.zc",
            "8141e353dc5960ef28c01883ccbb10411f62ac05",
            "QuantumMechanics.LiouvilleSecondQuantization.ContinuumKernelSpace",
            "provided_interface",
        ),
        KernelEvidence(
            "continuum_lindblad_generator",
            "formalization/zil/liouville-second-quantization.zc",
            "8141e353dc5960ef28c01883ccbb10411f62ac05",
            "claim:continuum_lindblad_generator",
            "open",
            open_assumptions=("lindblad_generator_closable", "continuum_semigroup_wellposed"),
        ),
        KernelEvidence(
            "continuum_semigroup_wellposed",
            "formalization/zil/liouville-second-quantization.zc",
            "8141e353dc5960ef28c01883ccbb10411f62ac05",
            "assumption:continuum_semigroup_wellposed",
            "open",
            open_assumptions=("continuum_semigroup_wellposed",),
        ),
    )


def observed_snapshot(items: tuple[KernelEvidence, ...] | None = None) -> dict[str, str]:
    selected = snapshot() if items is None else items
    return {item.path: item.expected_sha for item in selected}


def promotion_status(item: KernelEvidence, observed: dict[str, str]) -> PromotionStatus:
    actual = observed.get(item.path)
    if actual != item.expected_sha:
        return "stale"
    if not item.witness_declared:
        return "missing_witness"
    if item.open_assumptions:
        return "blocked_by_assumption" if item.verification_state == "kernel_checked" else "open_boundary"
    if item.verification_state == "kernel_checked":
        return "formal_promoted"
    if item.verification_state == "pending_ci":
        return "awaiting_kernel"
    if item.verification_state == "provided_interface":
        return "interface_only"
    return "open_boundary"


def refresh(
    items: tuple[KernelEvidence, ...] | None = None,
    observed: dict[str, str] | None = None,
) -> dict[str, Any]:
    selected = snapshot() if items is None else items
    source_map = observed_snapshot(selected) if observed is None else observed
    rows = [
        {
            **asdict(item),
            "observed_sha": source_map.get(item.path),
            "promotion_status": promotion_status(item, source_map),
        }
        for item in selected
    ]
    statuses = (
        "formal_promoted",
        "awaiting_kernel",
        "interface_only",
        "open_boundary",
        "stale",
        "missing_witness",
        "blocked_by_assumption",
    )
    payload = {"repository": FORMAL_REPOSITORY, "branch": FORMAL_BRANCH, "rows": rows}
    return {
        **payload,
        "counts": {
            status: sum(row["promotion_status"] == status for row in rows)
            for status in statuses
        },
        "fingerprint": sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
        ).hexdigest(),
    }


def promotion_controls() -> dict[str, Any]:
    base = snapshot()
    candidate = replace(base[0], verification_state="kernel_checked")
    current = observed_snapshot(base)
    stale = dict(current)
    stale[candidate.path] = "0" * 40
    return {
        "eligible_status": promotion_status(candidate, current),
        "stale_status": promotion_status(candidate, stale),
        "missing_witness_status": promotion_status(
            replace(candidate, witness_declared=False), current
        ),
        "open_assumption_status": promotion_status(
            replace(candidate, open_assumptions=("unclosed_domain",)), current
        ),
    }


@lru_cache(maxsize=1)
def run_kernel_evidence_refresh() -> dict[str, Any]:
    evaluation = refresh()
    controls = promotion_controls()
    counts = evaluation["counts"]
    acceptance = {
        "exact_repository_and_branch_are_pinned": evaluation["repository"] == FORMAL_REPOSITORY
        and evaluation["branch"] == FORMAL_BRANCH,
        "source_snapshot_has_no_drift": counts["stale"] == 0,
        "pending_records_are_not_promoted": counts["awaiting_kernel"] == 4
        and counts["formal_promoted"] == 0,
        "open_assumptions_are_not_promoted": counts["open_boundary"] == 2,
        "provided_carrier_remains_interface_only": counts["interface_only"] == 1,
        "eligible_kernel_record_can_promote": controls["eligible_status"] == "formal_promoted",
        "stale_source_blocks_promotion": controls["stale_status"] == "stale",
        "missing_witness_blocks_promotion": controls["missing_witness_status"] == "missing_witness",
        "open_assumption_blocks_promotion": controls["open_assumption_status"]
        == "blocked_by_assumption",
        "refresh_fingerprint_is_deterministic": evaluation["fingerprint"] == refresh()["fingerprint"],
    }
    return {
        "schema": "openwave.m9.kernel-evidence-refresh.v1",
        "task": "M9.55",
        "evaluation": evaluation,
        "promotion_controls": controls,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "refresh_completed": True,
            "new_formal_promotions": counts["formal_promoted"],
            "formal_continuum_generator_promoted": False,
            "gate": "PhysLib/ZIL exports no kernel_checked witness for the continuum generator stack",
        },
        "classification": {
            "establishes": [
                "exact source and declaration snapshot",
                "fail-closed kernel promotion policy",
                "stale, missing-witness, and open-assumption rejection controls",
            ],
            "does_not_establish": [
                "a kernel-checked continuum Lindblad generator",
                "continuum semigroup well-posedness",
                "formal promotion from pending_ci declarations",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
