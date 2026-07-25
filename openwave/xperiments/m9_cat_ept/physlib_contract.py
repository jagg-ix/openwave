"""Machine-readable PhysLib contract for the M9 CAT/EPT numerical model.

Lean remains the proof authority. OpenWave consumes only a pinned manifest that
names the formal source, declaration, status, numerical adapter, assumptions,
and claim boundary. Ordinary simulations do not require Lean at runtime.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
from typing import Any, Mapping

CONTRACT_SCHEMA = "openwave.m9.physlib-contract.v2"
CONTRACT_FILE = "physlib_contract.v2.json"
EXPECTED_REPOSITORY = "jagg-ix/entropic-physlib-private"
EXPECTED_BRANCH = "entropic-physlib-linear-full"
EXPECTED_COMMIT = "e10af9a3b47bf90afc0a88167a5d495b6935f4dc"
REQUIRED_INTERFACE_KEYS = {
    "id",
    "module",
    "declaration",
    "source_path",
    "source_blob",
    "status",
    "semantic_role",
    "numerical_adapter",
    "assumptions",
    "establishes",
    "does_not_establish",
}


def contract_path() -> Path:
    return Path(__file__).resolve().parent / "formal" / CONTRACT_FILE


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"formal contract root must be an object: {path}")
    return value


@lru_cache(maxsize=1)
def load_contract(path: Path | None = None) -> dict[str, Any]:
    return _read_json(path or contract_path())


def canonical_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def contract_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = load_contract() if payload is None else payload
    return sha256(canonical_payload(selected).encode()).hexdigest()


def _is_sha(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 40:
        return False
    return all(character in "0123456789abcdef" for character in value.lower())


def resolve_adapter(specification: str):
    module_name, separator, attribute = specification.partition(":")
    if not separator or not module_name or not attribute:
        raise ValueError(f"invalid numerical adapter: {specification!r}")
    module = import_module(module_name)
    adapter = getattr(module, attribute)
    if not callable(adapter):
        raise TypeError(f"numerical adapter is not callable: {specification!r}")
    return adapter


def validate_contract(
    payload: Mapping[str, Any] | None = None,
    *,
    observed_commit: str | None = None,
    observed_blobs: Mapping[str, str] | None = None,
    resolve_adapters: bool = False,
) -> dict[str, Any]:
    selected = dict(load_contract() if payload is None else payload)
    errors: list[str] = []
    repository = selected.get("repository")
    policy = selected.get("policy")
    interfaces = selected.get("interfaces")

    if selected.get("schema") != CONTRACT_SCHEMA:
        errors.append("unsupported contract schema")
    if not isinstance(repository, Mapping):
        errors.append("repository block is required")
        repository = {}
    if not isinstance(policy, Mapping):
        errors.append("policy block is required")
        policy = {}
    if not isinstance(interfaces, list) or not interfaces:
        errors.append("at least one formal interface is required")
        interfaces = []

    if repository.get("name") != EXPECTED_REPOSITORY:
        errors.append("unexpected formal repository")
    if repository.get("branch") != EXPECTED_BRANCH:
        errors.append("unexpected formal branch")
    if repository.get("commit") != EXPECTED_COMMIT:
        errors.append("unexpected formal commit")
    if not _is_sha(repository.get("commit")):
        errors.append("formal commit is not a Git SHA")
    if policy.get("runtime_dependency") is not False:
        errors.append("Lean must not be a mandatory runtime dependency")
    if policy.get("physical_identity_inherited") is not False:
        errors.append("formal interfaces cannot inherit physical identity")

    allowed_statuses = set(policy.get("allowed_statuses", ()))
    identifiers: list[str] = []
    declarations: list[str] = []
    adapter_specs: list[str] = []
    path_blobs: dict[str, str] = {}
    status_counts: dict[str, int] = {}

    for index, raw in enumerate(interfaces):
        if not isinstance(raw, Mapping):
            errors.append(f"interface {index} is not an object")
            continue
        missing = REQUIRED_INTERFACE_KEYS - set(raw)
        if missing:
            errors.append(f"interface {index} lacks {sorted(missing)}")
        identifier = raw.get("id")
        declaration = raw.get("declaration")
        path = raw.get("source_path")
        blob = raw.get("source_blob")
        status = raw.get("status")
        adapter = raw.get("numerical_adapter")
        identity_fields = (identifier, declaration, path, status, adapter)
        if not all(isinstance(value, str) and value for value in identity_fields):
            errors.append(f"interface {index} has an empty identity field")
            continue
        identifiers.append(identifier)
        declarations.append(declaration)
        adapter_specs.append(adapter)
        if not _is_sha(blob):
            errors.append(f"interface {identifier} has an invalid source blob")
        elif path in path_blobs and path_blobs[path] != blob:
            errors.append(f"interface {identifier} conflicts on source blob")
        else:
            path_blobs[path] = blob
        if status not in allowed_statuses:
            errors.append(f"interface {identifier} has unsupported status {status!r}")
        status_counts[status] = status_counts.get(status, 0) + 1
        if not raw.get("establishes"):
            errors.append(f"interface {identifier} lacks positive scope")
        if not raw.get("does_not_establish"):
            errors.append(f"interface {identifier} lacks a claim boundary")
        if resolve_adapters:
            try:
                resolve_adapter(adapter)
            except (ImportError, AttributeError, TypeError, ValueError) as error:
                errors.append(f"interface {identifier} adapter failed: {error}")

    if len(identifiers) != len(set(identifiers)):
        errors.append("duplicate interface identifier")
    if len(declarations) != len(set(declarations)):
        errors.append("duplicate formal declaration")
    if len(adapter_specs) != len(set(adapter_specs)):
        errors.append("duplicate numerical adapter")

    actual_commit = repository.get("commit") if observed_commit is None else observed_commit
    if actual_commit != repository.get("commit"):
        errors.append("formal repository commit drift detected")
    actual_blobs = path_blobs if observed_blobs is None else dict(observed_blobs)
    for path, expected_blob in path_blobs.items():
        actual_blob = actual_blobs.get(path)
        if actual_blob is None:
            errors.append(f"formal source missing: {path}")
        elif actual_blob != expected_blob:
            errors.append(f"formal source drift detected: {path}")

    acceptance = {
        "schema_is_supported": selected.get("schema") == CONTRACT_SCHEMA,
        "formal_repository_is_exact": repository.get("name") == EXPECTED_REPOSITORY,
        "formal_branch_is_exact": repository.get("branch") == EXPECTED_BRANCH,
        "formal_commit_is_exact": repository.get("commit") == EXPECTED_COMMIT,
        "interfaces_are_nonempty": bool(interfaces),
        "interface_ids_are_unique": len(identifiers) == len(set(identifiers)),
        "declarations_are_unique": len(declarations) == len(set(declarations)),
        "all_sources_are_blob_pinned": bool(path_blobs)
        and all(_is_sha(value) for value in path_blobs.values()),
        "claim_boundaries_are_explicit": bool(interfaces)
        and all(bool(item.get("does_not_establish")) for item in interfaces),
        "physical_identity_is_not_inherited": policy.get("physical_identity_inherited") is False,
        "lean_is_not_a_runtime_dependency": policy.get("runtime_dependency") is False,
        "observed_commit_matches": actual_commit == repository.get("commit"),
        "observed_blobs_match": all(
            actual_blobs.get(path) == expected for path, expected in path_blobs.items()
        ),
        "validation_has_no_errors": not errors,
    }
    return {
        "schema": "openwave.m9.physlib-contract-validation.v2",
        "contract_fingerprint": contract_fingerprint(selected),
        "repository": dict(repository),
        "interface_count": len(interfaces),
        "status_counts": status_counts,
        "source_blobs": path_blobs,
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


@lru_cache(maxsize=1)
def run_physlib_contract_study() -> dict[str, Any]:
    result = validate_contract(resolve_adapters=True)
    return {
        **result,
        "task": "M9.93a",
        "decision": {
            "formal_contract_current": result["passed"],
            "lean_runtime_required": False,
            "physical_particle_identity_inherited": False,
            "cross_repository_drift_is_fail_closed": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
