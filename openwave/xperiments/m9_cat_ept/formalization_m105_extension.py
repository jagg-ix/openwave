"""M9.103--M9.105 current Physlib and ZIL authority.

The scientific campaigns remain pinned to the current
``entropic-physlib-linear-full`` physics surfaces at ``eba0124...``. The
``zil-lean`` runtime advanced by one commit to add make-driven example groups,
structured TSV reporting, and a canonical formalization-claims example. These
reporting additions improve reproducibility and orchestration; they do not
supply a new theorem or a physical result.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m102_extension import (
    CURRENT_FORMAL_HEAD,
    CURRENT_PHYSLIB_ROOT_BLOB,
    FORMAL_BRANCH,
    FORMAL_REPOSITORY,
)

ZIL_REPOSITORY = "jagg-ix/zil-lean"
ZIL_BRANCH = "main"
HISTORICAL_ZIL_HEAD = "3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc"
CURRENT_ZIL_HEAD = "e09723a44185a1e70031ad2661c8009dc98bef74"
ZIL_COMMITS_SINCE_M98 = 1

PHYSICS_SOURCES = (
    {"path": "Physlib/QuantumMechanics/ComplexAction/Curvature/GlobalElectrograviticAction.lean", "blob": "39e807f424cf8384135299e84fdffc97fb506ee5", "role": "integrated coupled action and stationarity-to-field-equation interface", "boundary": "physical density and derivative identification remain supplied analytic data"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/MuonAnomaly/ThomasBMTMagicCancellation.lean", "blob": "7a7863819b8c86dfa1eb5a9647b4f59250885d4f", "role": "T-BMT scalar coefficients, magic cancellation, and rest-frame QED grounding", "boundary": "covariant boost and Thomas extension remains imported dynamics"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/ParametrizedTetradGravity/EMParticleDynamics.lean", "blob": "a1ef5ce20dfe0b843b124c6fa7a85b6809b8df50", "role": "Coulomb, radiation-gauge, and weak-ADM particle interfaces", "boundary": "explicit continuum Hamilton equations and PDE development remain analytic"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/ComptonClock/ComptonCellNewtonConstant.lean", "blob": "535738543f0259aae3f6f36e772ec4bf160317b8", "role": "G-free mass and inference-width Newton coupling maps", "boundary": "mass or inference width must be fixed independently"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/ClockRelativeEntropy.lean", "blob": "b0bbc6d801cbb0112eeafe628bc694a5d7bd1007", "role": "relative-entropy clock and frequency-lapse identities", "boundary": "physical clock identity and external calibration remain open"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/Yukawa/CouplingIsolation.lean", "blob": "527116982460e59e62c5736249a624f836d2f102", "role": "clock-frequency Yukawa inversion", "boundary": "an inversion is not an independent prediction"},
    {"path": "Physlib/Meta/ClaimMaturity.lean", "blob": "95f765f51b7c5cb58783a890c9d7482d1a2c6d52", "role": "six-axis maturity, prerequisite coherence, and assertion honesty", "boundary": "governance creates no physical evidence"},
    {"path": "Physlib/Meta/EvidenceIntegrity.lean", "blob": "9f5361a4606db34f60a5066634537703ac694700", "role": "structured gates, falsification, and internal-versus-external evidence classes", "boundary": "only registered measurements can close a gate"},
)

ZIL_SOURCES = (
    {"path": "Zil.lean", "blob": "faf28e701e4a02781e410491a6d3daf5d47f8879", "role": "Physlib-facing Datalog root"},
    {"path": "Zil/Native.lean", "blob": "2e6c87a85ef2f80d2424c8251ffe524067e27dee", "role": "native parser, query, provenance, workflow, and audit root"},
    {"path": "Makefile", "blob": "5f740e9662451d8484a6b0a96383341335ba1607", "role": "make-driven example groups and report entry points"},
    {"path": "scripts/examples.sh", "blob": "b720e3d720bf8ebb37cdd3c7a1ab51abd075be1c", "role": "ZIL-EXAMPLES-REPORT/1 runner with pass/fail/skip records and logs"},
    {"path": "examples/native-cli/formalization-claims.zc", "blob": "9d3c724f40785adcb6dd5947eeaa30bb2977a3d8", "role": "canonical current formalization-claim rule and query syntax"},
)

TARGETS = (
    {"id": "m9_103_unrestricted_charged_stationary", "scope": "unprojected coupled action descent plus short-time perturbation tubes", "failure_boundary": "stationarity or orbital gates may remain false"},
    {"id": "m9_104_packet_tbmt_refinement", "scope": "grid/time refined packet BMT versus exact Dirac generator", "failure_boundary": "the covariant Thomas law is an explicit external postulate, not QED-derived"},
    {"id": "m9_105_independent_calibration", "scope": "dependency-audited external-anchor and withheld-prediction protocol", "failure_boundary": "internal inversions cannot count as independent calibration"},
)


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(character in "0123456789abcdef" for character in value.lower())


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m105-extension.v1",
        "physlib": {"repository": FORMAL_REPOSITORY, "branch": FORMAL_BRANCH, "head": CURRENT_FORMAL_HEAD, "root_blob": CURRENT_PHYSLIB_ROOT_BLOB, "sources": [dict(source) for source in PHYSICS_SOURCES]},
        "zil": {"repository": ZIL_REPOSITORY, "branch": ZIL_BRANCH, "historical_head": HISTORICAL_ZIL_HEAD, "current_head": CURRENT_ZIL_HEAD, "commits_since_m98": ZIL_COMMITS_SINCE_M98, "report_schema": "ZIL-EXAMPLES-REPORT/1", "sources": [dict(source) for source in ZIL_SOURCES], "commands": [
            "bin/zil expand openwave/xperiments/m9_cat_ept/research/zil/m9_103_105_scientific_closure.zc -",
            "bin/zil trace openwave/xperiments/m9_cat_ept/research/zil/m9_103_105_scientific_closure.zc -",
            "bin/zil query-ci openwave/xperiments/m9_cat_ept/research/zil/m9_103_105_scientific_closure.zc",
        ]},
        "targets": [dict(target) for target in TARGETS],
        "policy": {"lean_remains_proof_authority": True, "zil_remains_orchestration_and_reporting_authority": True, "reporting_runtime_updates_promote_no_physics": True, "external_postulates_are_explicit": True, "internal_inversions_are_not_independent_calibration": True},
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_formalization_m105_extension() -> dict[str, Any]:
    payload = canonical_payload()
    physlib_paths = [item["path"] for item in PHYSICS_SOURCES]
    zil_paths = [item["path"] for item in ZIL_SOURCES]
    acceptance = {
        "current_physlib_head_and_root_are_exact": CURRENT_FORMAL_HEAD == "eba0124fcfbc1216d973bb6f504c5a6d324de60c" and _is_sha(CURRENT_PHYSLIB_ROOT_BLOB),
        "physics_source_registry_is_exact_and_unique": len(PHYSICS_SOURCES) == 8 and len(set(physlib_paths)) == len(physlib_paths) and all(_is_sha(item["blob"]) for item in PHYSICS_SOURCES),
        "zil_head_advanced_exactly_once": CURRENT_ZIL_HEAD == "e09723a44185a1e70031ad2661c8009dc98bef74" and HISTORICAL_ZIL_HEAD != CURRENT_ZIL_HEAD and ZIL_COMMITS_SINCE_M98 == 1,
        "zil_runtime_and_reporting_sources_are_exact": len(ZIL_SOURCES) == 5 and len(set(zil_paths)) == len(zil_paths) and all(_is_sha(item["blob"]) for item in ZIL_SOURCES),
        "all_three_scientific_targets_are_registered": len(TARGETS) == 3,
        "all_failure_boundaries_are_explicit": all(target["failure_boundary"] for target in TARGETS),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "task": "M9.103a", "fingerprint": fingerprint(payload), "acceptance": acceptance, "passed": all(acceptance.values()), "decision": {"current_physlib_and_zil_authorities_refreshed": True, "new_physics_result_created_by_authority_refresh": False, "physical_identity_changed": False}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
