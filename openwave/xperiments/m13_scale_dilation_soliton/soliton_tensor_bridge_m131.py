"""Scale transport of M11 pointwise solitons and infinite-mode tensor cutoffs."""
from __future__ import annotations
import math
import numpy as np
from openwave.xperiments.m11_cat_ept_soliton_qdo.pointwise_soliton_carrier_m111 import PointwiseSolitonConfig,construct_pointwise_soliton,run_pointwise_soliton_study
from openwave.xperiments.m11_cat_ept_soliton_qdo.liouville_soliton_tensor_m112 import LiouvilleTensorConfig,construct_liouville_tensor,run_liouville_tensor_study
from openwave.xperiments.m12_particle_zoo.electroweak_lepton_neutrino_m122 import LEPTON_MASSES_MEV
from openwave.xperiments.m12_particle_zoo.model_registration import run_particle_zoo_model_study
from .scale_geometry_m131 import scale_distance

def _width(x,rho):
    norm=float(np.trapezoid(rho,x)); mean=float(np.trapezoid(x*rho,x)/norm)
    return math.sqrt(max(float(np.trapezoid((x-mean)**2*rho,x)/norm),0.))

def run_soliton_tensor_bridge(rungs=(0.,.5,1.,1.5),grid=1025,half=12.,width=1.,modes=96):
    scales=np.asarray([2.**r for r in rungs]); norms=[]; widths=[]; residual=[]; trace=[]; purity=[]; mineig=[]; retained=[]
    tc=LiouvilleTensorConfig(modes,(16,32,64,modes),3)
    for scale in scales:
        sc=PointwiseSolitonConfig(grid_points=grid,half_length=half,inverse_width=width*float(scale))
        state=construct_pointwise_soliton(sc)
        norms.append(np.trapezoid(state.density,state.x)); widths.append(_width(state.x,state.density)); residual.append(np.max(np.abs(state.stationary_residual())))
        tensor=construct_liouville_tensor(tc,sc); rho=tensor.density_matrix; eig=np.linalg.eigvalsh(rho)
        trace.append(abs(np.trace(rho)-1)); purity.append(np.linalg.norm(rho@rho-rho)); mineig.append(eig.min()); retained.append(tensor.retained_probability)
    ws=np.asarray(widths)*scales
    masses=np.asarray([LEPTON_MASSES_MEV[n] for n in ("electron","muon","tau")]); labels=1/masses; errors=[]
    for i in range(3):
        for j in range(i+1,3): errors.append(abs(scale_distance(float(labels[i]),float(labels[j]))-abs(math.log(float(masses[j]/masses[i])))))
    add=abs(scale_distance(float(labels[0]),float(labels[2]))-scale_distance(float(labels[0]),float(labels[1]))-scale_distance(float(labels[1]),float(labels[2])))
    d={"soliton_norm_error":float(np.max(abs(np.asarray(norms)-1))),"soliton_residual":float(np.max(residual)),
       "soliton_width_error":float(np.max(abs(ws-ws[0]))),
       "soliton_metric_error":float(np.max(abs([scale_distance(float(s),1) for s in scales]-np.asarray(rungs)*math.log(2)))),
       "tensor_trace_error":float(np.max(trace)),"tensor_purity_error":float(np.max(purity)),
       "tensor_min_eigenvalue":float(np.min(mineig)),"tensor_min_retained":float(np.min(retained)),
       "particle_metric_error":max(errors),"particle_additivity_error":add,"particle_masses_ordered":bool(np.all(np.diff(masses)>0)),
       "prior_layers":{"m11_pointwise":bool(run_pointwise_soliton_study()["passed"]),"m11_liouville":bool(run_liouville_tensor_study()["passed"]),"m12_particle_zoo":bool(run_particle_zoo_model_study()["passed"])}}
    campaign={"rungs":list(rungs),"scale_factors":scales.tolist(),"pointwise_widths":list(map(float,widths)),"tensor_retained_probability":list(map(float,retained)),"particle_mass_inputs_mev":masses.tolist()}
    return d,campaign
