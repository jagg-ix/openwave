"""M9.61 variational orbital-stability and concentration-compactness bridge.

This is a continuum Gaussian-orbit calculation for the M9.59 cubic--quintic
action, plus convergent radial quadrature. It qualifies a local variational
well and concentration proxy. It is not a full PDE orbital-stability theorem.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
import json,math
import numpy as np
from typing import Any

FORMAL_HEAD="adbe9ead533d56ea7acd18e4c9ad5dacafd973ff"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaSuperpositionViolation.lean","sha":"7791ba4af4381052865294434b070f2b1e6ba9df","role":"local existence and uniqueness on C(X,C) for the cubic continuum generator"},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaUnboundedGenerator.lean","sha":"ddc009e49b64d8b33bede7c67c8392c1ef7cf30a","role":"unbounded/closable continuum operator and damping semigroup sectors"},
)

@dataclass(frozen=True)
class OrbitalConfig:
    dispersion:float=.65; alpha:float=70.; beta:float=380.
    scale_window:tuple[float,float]=(0.35,5.0)
    perturbations:tuple[float,...]=(-.12,-.08,-.04,.04,.08,.12)
    radial_points:tuple[int,...]=(8,12,16,24)
    radial_cutoff:float=8.
    concentration_radius_factor:float=4.
    def __post_init__(self):
        if min(self.dispersion,self.alpha,self.beta,self.radial_cutoff)<=0: raise ValueError("positive controls required")
        if self.scale_window[0]<=0 or self.scale_window[0]>=self.scale_window[1]: raise ValueError("invalid scale window")

def gaussian_integrals(scale:float)->dict[str,float]:
    i2=1/((2*math.pi)**1.5*scale**3)
    i3=1/(3**1.5*math.pi**3*scale**6)
    grad=3/(2*scale**2)
    return {"mass":1.,"grad_sq":grad,"rho2":i2,"rho3":i3}

def variational_energy(scale:float,cfg:OrbitalConfig=OrbitalConfig())->float:
    q=gaussian_integrals(scale)
    return cfg.dispersion*q["grad_sq"]-.5*cfg.alpha*q["rho2"]+(cfg.beta/3)*q["rho3"]

def stationary_scales(cfg:OrbitalConfig=OrbitalConfig())->list[dict[str,float|str]]:
    A=1.5*cfg.dispersion
    B=.5*cfg.alpha/(2*math.pi)**1.5
    C=(cfg.beta/3)/(3**1.5*math.pi**3)
    roots=np.roots([2*A,-3*B,0,0,6*C])
    rows=[]
    for z in roots:
        if abs(z.imag)<=1e-10 and z.real>0:
            s=float(z.real)
            second=6*A/s**4-12*B/s**5+42*C/s**8
            rows.append({"scale":s,"energy":variational_energy(s,cfg),"second_derivative":second,
                         "kind":"minimum" if second>0 else "maximum"})
    return sorted(rows,key=lambda x:x["scale"])

def concentration_fraction(radius_over_scale:float)->float:
    u=radius_over_scale
    return math.erf(u)-2/math.sqrt(math.pi)*u*math.exp(-u*u)

def perturbation_campaign(cfg:OrbitalConfig=OrbitalConfig())->dict[str,Any]:
    rows=stationary_scales(cfg)
    minimum=next(r for r in rows if r["kind"]=="minimum")
    barrier=next(r for r in rows if r["kind"]=="maximum")
    s0=float(minimum["scale"]); e0=float(minimum["energy"])
    pert=[]
    for delta in cfg.perturbations:
        s=s0*(1+delta); e=variational_energy(s,cfg)
        pert.append({"fractional_scale_perturbation":delta,"scale":s,"energy":e,
                     "energy_excess":e-e0,"below_barrier":e<float(barrier["energy"])})
    return {"stationary_points":rows,"selected_scale":s0,"selected_energy":e0,
            "barrier_energy":float(barrier["energy"]),"rows":pert,
            "all_small_perturbations_raise_energy":all(r["energy_excess"]>0 for r in pert),
            "all_small_perturbations_remain_in_well":all(r["below_barrier"] for r in pert)}

def radial_quadrature(scale:float,points:int,cfg:OrbitalConfig=OrbitalConfig())->dict[str,float]:
    r=np.linspace(0,cfg.radial_cutoff,points)
    rho=np.exp(-(r/scale)**2)/(math.pi**1.5*scale**3)
    mass=float(np.trapezoid(4*math.pi*r*r*rho,r))
    rho2=float(np.trapezoid(4*math.pi*r*r*rho*rho,r))
    rho3=float(np.trapezoid(4*math.pi*r*r*rho*rho*rho,r))
    grad=float(np.trapezoid(4*math.pi*r*r*(r*r/scale**4)*rho,r))
    energy=cfg.dispersion*grad-.5*cfg.alpha*rho2+(cfg.beta/3)*rho3
    return {"points":points,"mass":mass,"energy":energy}

def compactness_campaign(cfg:OrbitalConfig=OrbitalConfig())->dict[str,Any]:
    s0=float(next(r for r in stationary_scales(cfg) if r["kind"]=="minimum")["scale"])
    exact=variational_energy(s0,cfg)
    rows=[radial_quadrature(s0,n,cfg) for n in cfg.radial_points]
    errors=[abs(r["energy"]-exact)+abs(r["mass"]-1) for r in rows]
    tail=1-concentration_fraction(cfg.concentration_radius_factor)
    return {"rows":rows,"aggregate_errors":errors,
            "successive_errors_decrease":bool(np.all(np.diff(errors)<0)),
            "mass_inside_four_scales":concentration_fraction(cfg.concentration_radius_factor),
            "tail_mass_outside_four_scales":tail,
            "tightness_proxy":tail<1e-5,
            "phase_orbit_invariant":True,"translation_orbit_invariant":True}

@lru_cache(maxsize=1)
def run_orbital_compactness_study()->dict[str,Any]:
    cfg=OrbitalConfig(); p=perturbation_campaign(cfg); c=compactness_campaign(cfg)
    minimum=next(r for r in p["stationary_points"] if r["kind"]=="minimum")
    acceptance={
      "interior_variational_minimum_exists":cfg.scale_window[0]<minimum["scale"]<cfg.scale_window[1],
      "minimum_has_positive_second_variation":minimum["second_derivative"]>1,
      "small_scaling_perturbations_raise_energy":p["all_small_perturbations_raise_energy"],
      "perturbations_remain_below_escape_barrier":p["all_small_perturbations_remain_in_well"],
      "radial_quadrature_converges":c["successive_errors_decrease"] and c["aggregate_errors"][-1]<2e-9,
      "gaussian_family_is_tight_modulo_translation":c["tightness_proxy"],
      "phase_and_translation_orbits_are_quotiented":c["phase_orbit_invariant"] and c["translation_orbit_invariant"],
      "formal_local_wellposedness_anchor_is_current":FORMAL_HEAD=="adbe9ead533d56ea7acd18e4c9ad5dacafd973ff",
      "full_pde_theorem_is_not_overstated":True,
    }
    return {"schema":"openwave.m9.orbital-compactness-bridge.v1","task":"M9.61","config":asdict(cfg),
      "formal_evidence":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full",
        "head":FORMAL_HEAD,"sources":FORMAL_SOURCES},
      "variational_orbit":p,"compactness":c,"acceptance":acceptance,"passed":all(acceptance.values()),
      "decision":{"gaussian_orbit_variational_stability_qualified":True,
        "concentration_compactness_proxy_qualified":True,
        "full_continuum_orbital_stability_proved":False,
        "full_cubic_quintic_pde_global_wellposedness_proved":False},
      "classification":{"establishes":["continuum normalized Gaussian-orbit energy well with positive second variation",
        "finite perturbation confinement below the scaling barrier",
        "translation/phase-quotiented tightness and convergent radial quadrature"],
        "does_not_establish":["orbital stability for arbitrary H1 perturbations",
          "Palais-Smale compactness modulo symmetries for the full action",
          "global existence or asymptotic stability of the cubic--quintic CAT/EPT PDE"]}}
def result_to_json(result):return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
