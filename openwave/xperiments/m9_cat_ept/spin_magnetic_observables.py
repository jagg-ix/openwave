"""M9.29: field-derived spin, Pauli magnetic moment, and double-cover controls."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

ComplexArray=NDArray[np.complex128]
RealArray=NDArray[np.float64]

@dataclass(frozen=True)
class SpinParameters:
    half_width: float=6.0
    points: int=301
    width: float=1.0
    charge: float=1.0
    mass: float=1.0
    def __post_init__(self)->None:
        if self.half_width<=0 or self.width<=0 or self.mass<=0: raise ValueError("positive half_width, width, and mass required")
        if self.points<101 or self.points%2==0: raise ValueError("odd grid with at least 101 points required")

def grid(p:SpinParameters)->tuple[RealArray,RealArray,float]:
    axis=np.linspace(-p.half_width,p.half_width,p.points); dx=float(axis[1]-axis[0])
    x,y=np.meshgrid(axis,axis,indexing="xy"); return x,y,dx

def localized_spinor(p:SpinParameters,*,spin:int=1,global_phase:float=0.0)->ComplexArray:
    if spin not in (-1,1): raise ValueError("spin must be -1 or +1")
    x,y,dx=grid(p); rho=np.exp(-(x*x+y*y)/(2*p.width*p.width)); rho/=float(np.sum(rho)*dx*dx)
    amplitude=np.sqrt(rho)*np.exp(1j*global_phase); field=np.zeros((2,p.points,p.points),dtype=np.complex128)
    field[0 if spin==1 else 1]=amplitude; return field

def density(field:ComplexArray)->RealArray: return np.sum(np.abs(field)**2,axis=0).real

def spin_density_z(field:ComplexArray)->RealArray: return .5*(np.abs(field[0])**2-np.abs(field[1])**2).real

def pauli_magnetization_current(field:ComplexArray,p:SpinParameters)->tuple[RealArray,RealArray]:
    _,_,dx=grid(p); magnetization=(p.charge/p.mass)*spin_density_z(field)
    dy,dx_field=np.gradient(magnetization,dx,dx); return dy,-dx_field

def integrate(values:RealArray,dx:float)->float: return float(np.sum(values)*dx*dx)

def field_observables(field:ComplexArray,p:SpinParameters)->dict[str,float]:
    x,y,dx=grid(p); rho=density(field); spin_z=integrate(spin_density_z(field),dx)
    current_x,current_y=pauli_magnetization_current(field,p)
    moment_z=.5*integrate(x*current_y-y*current_x,dx)
    dy0,dx0=np.gradient(field[0],dx,dx); dy1,dx1=np.gradient(field[1],dx,dx)
    orbital=((np.conj(field[0])*(-1j*(x*dy0-y*dx0)))+(np.conj(field[1])*(-1j*(x*dy1-y*dx1)))).real
    orbital_z=integrate(orbital,dx)
    return {"norm":integrate(rho,dx),"spin_z":spin_z,"magnetic_moment_z":moment_z,
            "orbital_z":orbital_z,"total_j_z":orbital_z+spin_z,"expected_pauli_moment":(p.charge/p.mass)*spin_z}

def spin_rotation(field:ComplexArray,angle:float)->ComplexArray:
    out=field.copy(); out[0]*=np.exp(-.5j*angle); out[1]*=np.exp(.5j*angle); return out

def relative_l2(a:ComplexArray,b:ComplexArray)->float: return float(np.linalg.norm(a-b)/max(np.linalg.norm(a),1e-15))

def resolution_study()->dict[str,Any]:
    points=(151,301,601); records=[]
    for n in points:
        p=SpinParameters(points=n); records.append(field_observables(localized_spinor(p),p))
    return {"points":points,"records":records}

@lru_cache(maxsize=1)
def run_spin_magnetic_study()->dict[str,Any]:
    p=SpinParameters(); field=localized_spinor(p); flipped=localized_spinor(p,spin=-1); phased=localized_spinor(p,global_phase=1.234)
    base=field_observables(field,p); negative=field_observables(flipped,p); phased_obs=field_observables(phased,p)
    two=spin_rotation(field,2*math.pi); four=spin_rotation(field,4*math.pi); two_obs=field_observables(two,p)
    resolution=resolution_study(); finest=resolution["records"][-1]
    acceptance={
      "normalized_localized_field":abs(base["norm"]-1)<=2e-12,
      "spin_half_integral":abs(base["spin_z"]-.5)<=2e-12,
      "pauli_moment_from_current":abs(base["magnetic_moment_z"]-base["expected_pauli_moment"])<=5e-4,
      "orbital_control_zero":abs(base["orbital_z"])<=2e-12,
      "spin_flip_reverses_observables":abs(negative["spin_z"]+base["spin_z"])<=2e-12 and abs(negative["magnetic_moment_z"]+base["magnetic_moment_z"])<=5e-4,
      "double_cover_return":relative_l2(two,-field)<=2e-12 and relative_l2(four,field)<=2e-12,
      "bilinears_return_after_two_pi":all(abs(two_obs[name]-base[name])<=2e-12 for name in ("norm","spin_z","orbital_z","total_j_z")),
      "global_phase_and_resolution_robust":abs(phased_obs["spin_z"]-base["spin_z"])<=2e-12 and abs(phased_obs["magnetic_moment_z"]-base["magnetic_moment_z"])<=5e-12 and abs(finest["magnetic_moment_z"]-.5)<=2e-4,
    }
    return {"schema":"openwave.m9.spin-magnetic-result.v1","task":"M9.29","parameters":asdict(p),
            "observables":base,"spin_down_observables":negative,
            "double_cover":{"two_pi_to_minus_state_error":relative_l2(two,-field),"four_pi_return_error":relative_l2(four,field),
                            "two_pi_bilinear_spin_error":abs(two_obs["spin_z"]-base["spin_z"])},
            "resolution":resolution,"acceptance":acceptance,"passed":all(acceptance.values()),
            "field_observable_control":True,"fermionic_exchange_statistics_established":False,
            "classification":{"establishes":["field-integrated spin","magnetic moment from Pauli current","2pi sign reversal and 4pi return"],
                              "does_not_establish":["exchange statistics","emergent electron g factor","stable 3D particle"]}}

def result_to_json(result:dict[str,Any])->str: return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
