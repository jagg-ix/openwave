"""Manifest-driven accelerator buffer and kernel adapter.

The adapter lowers a versioned simulation manifest into aligned flat device
buffers, deterministic field views, a validated kernel IR, generated source,
a NumPy reference backend, and a flat-buffer accelerator emulator.

The emulator is used for deterministic parity testing when no GPU runtime is
available. Hardware GPU execution is intentionally not claimed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
import math
from typing import Any, Literal, Mapping

import numpy as np
from numpy.typing import NDArray

DTypeName = Literal["float64", "complex128"]
SUPPORTED_DTYPES: dict[DTypeName, np.dtype[Any]] = {
    "float64": np.dtype(np.float64),
    "complex128": np.dtype(np.complex128),
}


@dataclass(frozen=True)
class DeviceField:
    name: str
    dtype: DTypeName
    shape: tuple[int, ...]
    role: str

    def __post_init__(self) -> None:
        if not self.name or self.dtype not in SUPPORTED_DTYPES:
            raise ValueError("supported named field required")
        if not self.shape or any(size <= 0 for size in self.shape):
            raise ValueError("concrete positive device shape required")


@dataclass(frozen=True)
class KernelIR:
    name: str
    op: str
    reads: tuple[str, ...]
    writes: tuple[str, ...]
    parameters: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name or not self.op or not self.writes:
            raise ValueError("named writing kernel required")
        if len(self.writes) != len(set(self.writes)):
            raise ValueError("duplicate writes")


@dataclass(frozen=True)
class DeviceManifest:
    name: str
    version: str
    fields: tuple[DeviceField, ...]
    kernels: tuple[KernelIR, ...]
    parameters: tuple[str, ...]

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "fields": [asdict(item) for item in self.fields],
            "kernels": [asdict(item) for item in self.kernels],
            "parameters": list(self.parameters),
        }

    def fingerprint(self) -> str:
        payload = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class BufferSlice:
    field: str
    dtype: DTypeName
    shape: tuple[int, ...]
    offset_bytes: int
    size_bytes: int
    alignment: int


@dataclass(frozen=True)
class CompiledDevicePlan:
    manifest: DeviceManifest
    slices: tuple[BufferSlice, ...]
    total_bytes: int
    generated_source: str
    fingerprint: str

    def slice_for(self, field: str) -> BufferSlice:
        for item in self.slices:
            if item.field == field:
                return item
        raise KeyError(field)


class AdapterError(ValueError):
    pass


def _align(offset: int, alignment: int) -> int:
    return ((offset + alignment - 1) // alignment) * alignment


def validate_manifest(manifest: DeviceManifest) -> None:
    field_names = [item.name for item in manifest.fields]
    kernel_names = [item.name for item in manifest.kernels]
    if len(field_names) != len(set(field_names)):
        raise AdapterError("duplicate field")
    if len(kernel_names) != len(set(kernel_names)):
        raise AdapterError("duplicate kernel")
    fields = set(field_names)
    parameters = set(manifest.parameters)
    writers: dict[str, str] = {}
    supported_ops = {"metric_source", "phase_step", "loss_transfer", "observe"}
    for kernel in manifest.kernels:
        if kernel.op not in supported_ops:
            raise AdapterError(f"unsupported op {kernel.op}")
        missing = (set(kernel.reads) | set(kernel.writes)) - fields
        if missing:
            raise AdapterError(f"kernel {kernel.name} references unknown fields {sorted(missing)}")
        missing_parameters = set(kernel.parameters) - parameters
        if missing_parameters:
            raise AdapterError(
                f"kernel {kernel.name} references unknown parameters {sorted(missing_parameters)}"
            )
        for field in kernel.writes:
            previous = writers.get(field)
            if previous is not None and kernel.op != "observe":
                if field not in kernel.reads:
                    raise AdapterError(
                        f"implicit overwrite of {field} by {kernel.name} after {previous}"
                    )
            writers[field] = kernel.name


def generate_source(manifest: DeviceManifest) -> str:
    lines = [
        f"# generated accelerator source for {manifest.name}@{manifest.version}",
        "# backend contract: one index per lattice element",
    ]
    for field in manifest.fields:
        lines.append(
            f"field {field.name}: {field.dtype}[{','.join(map(str, field.shape))}] role={field.role}"
        )
    for kernel in manifest.kernels:
        lines.append(
            f"kernel {kernel.name} op={kernel.op} reads={','.join(kernel.reads)} "
            f"writes={','.join(kernel.writes)} params={','.join(kernel.parameters)}"
        )
    return "\n".join(lines) + "\n"


def compile_manifest(
    manifest: DeviceManifest,
    *,
    alignment: int = 64,
) -> CompiledDevicePlan:
    if alignment <= 0 or alignment & (alignment - 1):
        raise AdapterError("alignment must be a positive power of two")
    validate_manifest(manifest)
    offset = 0
    slices = []
    for field in manifest.fields:
        dtype = SUPPORTED_DTYPES[field.dtype]
        offset = _align(offset, alignment)
        size = int(np.prod(field.shape)) * dtype.itemsize
        slices.append(
            BufferSlice(field.name, field.dtype, field.shape, offset, size, alignment)
        )
        offset += size
    total = _align(offset, alignment)
    source = generate_source(manifest)
    canonical = {
        "manifest": manifest.canonical_dict(),
        "slices": [asdict(item) for item in slices],
        "total_bytes": total,
        "source": source,
    }
    fingerprint = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return CompiledDevicePlan(manifest, tuple(slices), total, source, fingerprint)


class FlatDeviceBuffer:
    def __init__(self, plan: CompiledDevicePlan) -> None:
        self.plan = plan
        self.storage = np.zeros(plan.total_bytes, dtype=np.uint8)

    def view(self, field: str) -> NDArray[Any]:
        item = self.plan.slice_for(field)
        dtype = SUPPORTED_DTYPES[item.dtype]
        count = int(np.prod(item.shape))
        return np.ndarray(
            shape=(count,),
            dtype=dtype,
            buffer=self.storage,
            offset=item.offset_bytes,
        ).reshape(item.shape)

    def load(self, state: Mapping[str, NDArray[Any]]) -> None:
        expected = {item.name for item in self.plan.manifest.fields}
        if set(state) != expected:
            raise AdapterError("state fields do not match manifest")
        for item in self.plan.manifest.fields:
            value = np.asarray(state[item.name], dtype=SUPPORTED_DTYPES[item.dtype])
            if value.shape != item.shape:
                raise AdapterError(f"shape mismatch for {item.name}")
            self.view(item.name)[...] = value

    def export(self) -> dict[str, NDArray[Any]]:
        return {
            item.name: self.view(item.name).copy()
            for item in self.plan.manifest.fields
        }


def _execute_kernel(
    kernel: KernelIR,
    state: Mapping[str, NDArray[Any]],
    parameters: Mapping[str, float],
) -> None:
    if kernel.op == "metric_source":
        psi = state["psi"]
        density = np.abs(psi) ** 2
        state["metric"][...] = parameters["geometry_coupling"] * (
            density - float(np.mean(density))
        )
    elif kernel.op == "phase_step":
        phase = np.exp(
            -1j
            * parameters["dt"]
            * (parameters["omega"] + state["metric"])
        )
        state["psi"][...] *= phase
    elif kernel.op == "loss_transfer":
        psi = state["psi"]
        before = np.abs(psi) ** 2
        factor = math.exp(-parameters["loss_rate"] * parameters["dt"])
        psi[...] *= factor
        after = np.abs(psi) ** 2
        state["reservoir"][...] += before - after
        state["entropy"][...] += parameters["loss_rate"] * parameters["dt"]
    elif kernel.op == "observe":
        psi = state["psi"]
        state["observable"][0] = float(np.sum(np.abs(psi) ** 2))
        state["observable"][1] = float(np.sum(state["reservoir"]))
        state["observable"][2] = float(np.mean(state["entropy"]))
        state["observable"][3] = float(np.max(np.abs(state["metric"])))
    else:
        raise AdapterError(kernel.op)


def execute_numpy(
    plan: CompiledDevicePlan,
    state: Mapping[str, NDArray[Any]],
    parameters: Mapping[str, float],
) -> dict[str, NDArray[Any]]:
    working = {
        item.name: np.asarray(
            state[item.name], dtype=SUPPORTED_DTYPES[item.dtype]
        ).copy()
        for item in plan.manifest.fields
    }
    _validate_parameters(plan.manifest, parameters)
    for kernel in plan.manifest.kernels:
        _execute_kernel(kernel, working, parameters)
    return working


def execute_flat_device(
    plan: CompiledDevicePlan,
    state: Mapping[str, NDArray[Any]],
    parameters: Mapping[str, float],
) -> dict[str, NDArray[Any]]:
    _validate_parameters(plan.manifest, parameters)
    buffer = FlatDeviceBuffer(plan)
    buffer.load(state)
    views = {item.name: buffer.view(item.name) for item in plan.manifest.fields}
    for kernel in plan.manifest.kernels:
        _execute_kernel(kernel, views, parameters)
    return buffer.export()


def _validate_parameters(
    manifest: DeviceManifest,
    parameters: Mapping[str, float],
) -> None:
    if set(parameters) != set(manifest.parameters):
        raise AdapterError("parameter set does not match manifest")
    if not all(math.isfinite(float(value)) for value in parameters.values()):
        raise AdapterError("finite parameters required")


def reference_manifest(points: int = 64) -> DeviceManifest:
    return DeviceManifest(
        "cat-ept-accelerator-reference",
        "1.0",
        (
            DeviceField("psi", "complex128", (points,), "dynamic"),
            DeviceField("metric", "float64", (points,), "dynamic"),
            DeviceField("entropy", "float64", (points,), "ledger"),
            DeviceField("reservoir", "float64", (points,), "ledger"),
            DeviceField("observable", "float64", (4,), "observable"),
        ),
        (
            KernelIR(
                "metric_source",
                "metric_source",
                ("psi",),
                ("metric",),
                ("geometry_coupling",),
            ),
            KernelIR(
                "phase_step",
                "phase_step",
                ("psi", "metric"),
                ("psi",),
                ("dt", "omega"),
            ),
            KernelIR(
                "loss_transfer",
                "loss_transfer",
                ("psi", "reservoir", "entropy"),
                ("psi", "reservoir", "entropy"),
                ("dt", "loss_rate"),
            ),
            KernelIR(
                "observe",
                "observe",
                ("psi", "metric", "entropy", "reservoir"),
                ("observable",),
                (),
            ),
        ),
        ("dt", "omega", "loss_rate", "geometry_coupling"),
    )


def reference_state(manifest: DeviceManifest) -> dict[str, NDArray[Any]]:
    points = manifest.fields[0].shape[0]
    phase = np.linspace(0.0, 2.0 * math.pi, points, endpoint=False)
    psi = (1.0 + 0.2 * np.cos(phase)) * np.exp(0.35j * np.sin(phase))
    psi = psi.astype(np.complex128)
    psi /= math.sqrt(float(np.sum(np.abs(psi) ** 2)))
    return {
        "psi": psi,
        "metric": np.zeros(points, dtype=np.float64),
        "entropy": np.zeros(points, dtype=np.float64),
        "reservoir": np.zeros(points, dtype=np.float64),
        "observable": np.zeros(4, dtype=np.float64),
    }


def reference_parameters() -> dict[str, float]:
    return {
        "dt": 0.04,
        "omega": 0.7,
        "loss_rate": 0.12,
        "geometry_coupling": 0.25,
    }


@lru_cache(maxsize=1)
def run_gpu_adapter_study() -> dict[str, Any]:
    manifest = reference_manifest()
    plan = compile_manifest(manifest)
    state = reference_state(manifest)
    parameters = reference_parameters()
    numpy_result = execute_numpy(plan, state, parameters)
    device_result = execute_flat_device(plan, state, parameters)

    parity = {
        field.name: float(
            np.max(np.abs(numpy_result[field.name] - device_result[field.name]))
        )
        for field in manifest.fields
    }
    slices = [asdict(item) for item in plan.slices]
    offsets = [item["offset_bytes"] for item in slices]
    nonoverlap = all(
        slices[index]["offset_bytes"] + slices[index]["size_bytes"]
        <= slices[index + 1]["offset_bytes"]
        for index in range(len(slices) - 1)
    )

    unsupported_op_rejected = False
    try:
        compile_manifest(
            DeviceManifest(
                "bad",
                "1",
                manifest.fields,
                (KernelIR("bad", "unsupported", ("psi",), ("metric",), ()),),
                (),
            )
        )
    except AdapterError:
        unsupported_op_rejected = True

    malformed_state_rejected = False
    try:
        execute_flat_device(
            plan,
            {**state, "psi": np.zeros(3, dtype=np.complex128)},
            parameters,
        )
    except AdapterError:
        malformed_state_rejected = True

    second = compile_manifest(manifest)
    taichi_available = importlib.util.find_spec("taichi") is not None

    acceptance = {
        "manifest_compiles": len(plan.slices) == len(manifest.fields),
        "aligned_nonoverlapping_layout": (
            all(offset % 64 == 0 for offset in offsets) and nonoverlap
        ),
        "numpy_device_parity": max(parity.values()) <= 2e-15,
        "balance_observable_closes": bool(
            abs(device_result["observable"][0] + device_result["observable"][1] - 1.0)
            <= 2e-14
        ),
        "generated_source_is_deterministic": plan.generated_source
        == second.generated_source,
        "plan_fingerprint_is_deterministic": plan.fingerprint == second.fingerprint,
        "unsupported_ir_rejected": unsupported_op_rejected,
        "malformed_state_rejected": malformed_state_rejected,
    }
    return {
        "schema": "openwave.m9.gpu-adapter-result.v1",
        "task": "M9.38",
        "manifest_fingerprint": manifest.fingerprint(),
        "plan_fingerprint": plan.fingerprint,
        "total_bytes": plan.total_bytes,
        "buffer_slices": slices,
        "generated_source": plan.generated_source,
        "parity_max_error": parity,
        "final_observable": device_result["observable"].tolist(),
        "taichi_runtime_available": taichi_available,
        "hardware_gpu_executed": False,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "manifest-to-device buffer compilation",
                "deterministic aligned memory layouts",
                "validated kernel intermediate representation",
                "generated accelerator source contract",
                "flat-buffer/reference parity and balance ledgers",
            ],
            "does_not_establish": [
                "hardware GPU execution",
                "performance speedup",
                "Taichi or CUDA kernel compilation on every platform",
                "numerical equivalence for arbitrary theory kernels",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
