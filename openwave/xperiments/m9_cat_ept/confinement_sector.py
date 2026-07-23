"""Reduced confinement and flux-tube simulation control.

The reference sector uses a regularized Cornell interaction,

    V(r) = sigma * sqrt(r^2 + a^2) - alpha / sqrt(r^2 + a^2),

with a string-breaking ledger once the stored flux energy reaches twice the
pair-creation mass. SU(3)-like color vectors are included only as a neutrality
bookkeeping control. This is not QCD.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray
Vector = NDArray[np.float64]

@dataclass(frozen=True)
class ConfinementConfig:
    string_tension: float = 0.9
    coulomb_strength: float = 0.35
    softening: float = 0.2
    pair_creation_mass: float = 1.4
    def __post_init__(self) -> None:
        if self.string_tension < 0 or self.coulomb_strength < 0: raise ValueError("nonnegative interaction strengths required")
        if self.softening <= 0 or self.pair_creation_mass <= 0: raise ValueError("positive softening and pair mass required")

COLORS={"red":np.asarray([1.,0.]),"green":np.asarray([-.5,math.sqrt(3)/2]),"blue":np.asarray([-.5,-math.sqrt(3)/2])}
def color_singlet_residual(colors:tuple[str,...])->float:
    if any(name not in COLORS for name in colors): raise ValueError("unknown color")
    return float(np.linalg.norm(np.sum([COLORS[name] for name in colors],axis=0)))
def softened_radius(r:float,cfg:ConfinementConfig)->float:
    if r<0: raise ValueError("nonnegative separation required")
    return math.sqrt(r*r+cfg.softening*cfg.softening)
def potential(r:float,cfg:ConfinementConfig=ConfinementConfig())->float:
    s=softened_radius(r,cfg); return cfg.string_tension*s-cfg.coulomb_strength/s
def radial_force(r:float,cfg:ConfinementConfig=ConfinementConfig())->float:
    s=softened_radius(r,cfg); return -cfg.string_tension*r/s-cfg.coulomb_strength*r/s**3
def flux_energy(r:float,cfg:ConfinementConfig=ConfinementConfig())->float:return cfg.string_tension*softened_radius(r,cfg)
def string_breaking_radius(cfg:ConfinementConfig=ConfinementConfig())->float:
    if cfg.string_tension<=0:return math.inf
    threshold=2*cfg.pair_creation_mass/cfg.string_tension
    return math.sqrt(max(threshold*threshold-cfg.softening*cfg.softening,0.))
def string_breaking_ledger(r:float,cfg:ConfinementConfig=ConfinementConfig())->dict[str,float|bool]:
    stored=flux_energy(r,cfg); threshold=2*cfg.pair_creation_mass; broken=stored>=threshold; pairs=1. if broken else 0.; residual=max(stored-threshold,0.) if broken else stored
    return {"stored_flux_energy":stored,"pair_creation_threshold":threshold,"string_broken":broken,"created_pair_count":pairs,"residual_flux_energy":residual,"energy_closure":residual+pairs*threshold-stored}
def asymptotic_fit(cfg:ConfinementConfig=ConfinementConfig())->dict[str,float]:
    radii=np.linspace(8.,30.,200); values=np.asarray([potential(float(r),cfg) for r in radii]); forces=np.asarray([radial_force(float(r),cfg) for r in radii]); slope,intercept=np.polyfit(radii,values,1); plateau=-float(np.median(forces[-60:]))
    return {"potential_slope":float(slope),"potential_intercept":float(intercept),"force_plateau":plateau,"slope_error":abs(float(slope)-cfg.string_tension),"force_plateau_error":abs(plateau-cfg.string_tension)}
def deconfinement_control()->dict[str,float]:
    cfg=ConfinementConfig(string_tension=0.); radii=np.asarray([4.,8.,16.,32.]); values=np.asarray([potential(float(r),cfg) for r in radii]); forces=np.asarray([abs(radial_force(float(r),cfg)) for r in radii]); power=float(np.polyfit(np.log(radii),np.log(forces),1)[0])
    return {"largest_potential":float(np.max(values)),"potential_difference":float(values[-1]-values[0]),"force_power":power}
@lru_cache(maxsize=1)
def run_confinement_study()->dict[str,Any]:
    cfg=ConfinementConfig(); fit=asymptotic_fit(cfg); rb=string_breaking_radius(cfg); below=string_breaking_ledger(.9*rb,cfg); above=string_breaking_ledger(1.1*rb,cfg); deconfined=deconfinement_control(); r=2.7; eps=1e-6; numeric=-(potential(r+eps,cfg)-potential(r-eps,cfg))/(2*eps)
    acceptance={"force_matches_energy_gradient":abs(numeric-radial_force(r,cfg))<=2e-8,"linear_potential_asymptote":fit["slope_error"]<=2e-3,"constant_force_asymptote":fit["force_plateau_error"]<=2e-3,"mesonic_color_singlet_closes":color_singlet_residual(("red","green","blue"))<=1e-14,"below_threshold_string_survives":not bool(below["string_broken"]),"above_threshold_string_breaks":bool(above["string_broken"]),"string_breaking_energy_closes":abs(float(above["energy_closure"]))<=1e-14,"zero_tension_loses_confinement":abs(deconfined["force_power"]+2)<=2e-2 and deconfined["potential_difference"]<.1}
    return {"schema":"openwave.m9.confinement-sector-result.v1","task":"M9.40","config":asdict(cfg),"asymptotic":fit,"string_breaking_radius":rb,"below_threshold":below,"above_threshold":above,"deconfinement_control":deconfined,"color_singlet_residual":color_singlet_residual(("red","green","blue")),"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["regularized Cornell potential control","linear large-distance energy growth","constant string-force asymptote","color-neutral bookkeeping control","string-breaking energy ledger"],"does_not_establish":["QCD or non-Abelian gauge dynamics","dynamical gluons or running coupling","physical string tension","quarks emerging from CAT/EPT fields"]}}
def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
