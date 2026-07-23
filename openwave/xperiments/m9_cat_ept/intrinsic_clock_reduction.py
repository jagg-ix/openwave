"""M9.28: separate internal phase, entropic, and geometry clock channels."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]

@dataclass(frozen=True)
class ClockParameters:
    final_time: float = 10.0
    samples: int = 2001
    internal_frequency: float = 1.7
    mean_loss_rate: float = 0.11
    loss_modulation: float = 0.35
    loss_frequency: float = 0.73
    velocity_amplitude: float = 0.45
    velocity_frequency: float = 0.61
    phase_offset: float = 0.23
    def __post_init__(self) -> None:
        if self.final_time <= 0 or self.samples < 101: raise ValueError("positive final_time and at least 101 samples required")
        if self.internal_frequency < 0 or self.mean_loss_rate < 0: raise ValueError("frequency and loss rate must be nonnegative")
        if not 0 <= self.loss_modulation < 1: raise ValueError("loss_modulation must lie in [0,1)")
        if self.loss_frequency <= 0 or self.velocity_frequency <= 0: raise ValueError("modulation frequencies must be positive")
        if not 0 <= self.velocity_amplitude < 1: raise ValueError("velocity amplitude must lie in [0,1)")

def cumulative_trapezoid(values: RealArray, times: RealArray) -> RealArray:
    return np.concatenate((np.array([0.0]), np.cumsum(.5*(values[:-1]+values[1:])*np.diff(times))))

def loss_rate(times: RealArray, p: ClockParameters) -> RealArray:
    return p.mean_loss_rate*(1+p.loss_modulation*np.cos(p.loss_frequency*times))

def generate_clock_trace(p: ClockParameters=ClockParameters(), *, amplitude_scale: float=1.0) -> dict[str, RealArray|ComplexArray]:
    if amplitude_scale <= 0: raise ValueError("amplitude_scale must be positive")
    t=np.linspace(0,p.final_time,p.samples)
    rates=loss_rate(t,p); entropy=cumulative_trapezoid(rates,t)
    signal=amplitude_scale*np.exp(-entropy+1j*(p.phase_offset+p.internal_frequency*t))
    norm=np.abs(signal)**2
    velocity=p.velocity_amplitude*np.sin(p.velocity_frequency*t)
    lapse=np.sqrt(1-velocity**2)
    return {"time":t,"signal":signal,"norm":norm,"phase":np.unwrap(np.angle(signal)),
            "entropic_clock":-.5*np.log(norm/norm[0]),"geometry_clock":cumulative_trapezoid(lapse,t),
            "loss_rate":rates,"velocity":velocity,"lapse":lapse}

def slope(t: RealArray, values: RealArray) -> float: return float(np.polyfit(t,values,1)[0])

def affine_residual(reference: RealArray, candidate: RealArray) -> float:
    matrix=np.column_stack((reference,np.ones_like(reference)))
    coefficients,*_=np.linalg.lstsq(matrix,candidate,rcond=None)
    residual=candidate-matrix@coefficients
    return float(np.linalg.norm(residual)/(math.sqrt(candidate.size)*max(float(np.ptp(candidate)),np.finfo(float).eps)))

def rate_variation(t: RealArray, clock: RealArray) -> float:
    derivative=np.gradient(clock,t)
    return float(np.std(derivative)/max(abs(float(np.mean(derivative))),np.finfo(float).eps))

def zero_channel_controls() -> dict[str,float]:
    base=ClockParameters()
    zero_loss=ClockParameters(**{**asdict(base),"mean_loss_rate":0.0})
    zero_frequency=ClockParameters(**{**asdict(base),"internal_frequency":0.0})
    a=generate_clock_trace(zero_loss); b=generate_clock_trace(zero_frequency)
    return {"zero_loss_entropy_span":float(np.ptp(a["entropic_clock"])),"zero_loss_phase_span":float(np.ptp(a["phase"])),
            "zero_frequency_phase_span":float(np.ptp(b["phase"])),"zero_frequency_entropy_span":float(np.ptp(b["entropic_clock"]))}

@lru_cache(maxsize=1)
def run_intrinsic_clock_study() -> dict[str,Any]:
    p=ClockParameters(); trace=generate_clock_trace(p); scaled=generate_clock_trace(p,amplitude_scale=3.7)
    t=trace["time"]; phase=trace["phase"]; entropy=trace["entropic_clock"]; geometry=trace["geometry_clock"]
    phase_clock=(phase-phase[0])/p.internal_frequency
    entropy_residual=affine_residual(phase_clock,entropy); geometry_residual=affine_residual(phase_clock,geometry)
    controls=zero_channel_controls()
    acceptance={
      "internal_frequency_recovered":abs(slope(t,phase)-p.internal_frequency)<=2e-12,
      "phase_rigid_under_loss_modulation":rate_variation(t,phase)<=2e-12,
      "entropy_monotone":bool(np.all(np.diff(entropy)>=-2e-12)),
      "geometry_clock_monotone_and_subluminal":bool(np.all(np.diff(geometry)>=-2e-12)) and geometry[-1]<=t[-1]+2e-12,
      "channels_not_affinely_identical":entropy_residual>=1e-2 and geometry_residual>=1e-3,
      "zero_loss_separates_phase_from_entropy":controls["zero_loss_entropy_span"]<=2e-12 and controls["zero_loss_phase_span"]>=10,
      "zero_frequency_separates_entropy_from_phase":controls["zero_frequency_phase_span"]<=2e-12 and controls["zero_frequency_entropy_span"]>=.5,
      "global_amplitude_scale_invariant":float(np.max(np.abs(scaled["phase"]-phase)))<=2e-12 and float(np.max(np.abs(scaled["entropic_clock"]-entropy)))<=2e-12,
    }
    return {"schema":"openwave.m9.intrinsic-clock-result.v1","task":"M9.28","parameters":asdict(p),
            "recovered_internal_frequency":slope(t,phase),"recovered_mean_loss_slope":slope(t,entropy),
            "entropy_rate_variation":rate_variation(t,entropy),"geometry_rate_variation":rate_variation(t,geometry),
            "entropy_vs_phase_affine_residual":entropy_residual,"geometry_vs_phase_affine_residual":geometry_residual,
            "final":{"coordinate_time":float(t[-1]),"internal_phase":float(phase[-1]-phase[0]),
                     "entropic_clock":float(entropy[-1]),"geometry_clock":float(geometry[-1])},
            "zero_channel_controls":controls,"acceptance":acceptance,"passed":all(acceptance.values()),
            "intrinsic_clock_candidate":"reversible_internal_phase","physical_time_identified":False,
            "classification":{"establishes":["rigid reversible internal phase","positive nonuniform entropy monotone","separate geometry clock proxy"],
                              "does_not_establish":["physical time","particle Zitterbewegung","relativistic metric solution"]}}

def result_to_json(result: dict[str,Any]) -> str: return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
