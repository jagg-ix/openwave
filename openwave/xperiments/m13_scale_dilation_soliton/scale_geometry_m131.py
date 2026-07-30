"""Exact executable mirror of the CAT/EPT dilation and logarithmic scale line."""
from __future__ import annotations
import math
import numpy as np

def dilation_flow(generator: float, time: float) -> float:
    return math.exp(generator * time)

def scale_lagrangian(scale: float, velocity: float) -> float:
    return 0.5 * (velocity / scale) ** 2

def scale_distance(left: float, right: float) -> float:
    if left <= 0 or right <= 0:
        raise ValueError("positive scales required")
    return abs(math.log(left / right))

def run_scale_geometry(generator=.75, initial=1.3, multiplier=2.7,
                       times=(-1.,-.5,0.,.5,1.), steps=6, a0=.125,
                       rungs=(0.,.5,1.,1.5), schmidt=3., compton=1.,
                       energy=2.5, charge=3., charge_time=.4):
    t=np.asarray(times); lam=initial*np.exp(generator*t); vel=generator*lam; acc=generator**2*lam
    group=max(abs(dilation_flow(generator,float(a+b))-dilation_flow(generator,float(a))*dilation_flow(generator,float(b))) for a in t for b in t)
    inverse=max(abs(dilation_flow(generator,float(-a))*dilation_flow(generator,float(a))-1) for a in t)
    L=np.asarray([scale_lagrangian(x,v) for x,v in zip(lam,vel)])
    Lm=np.asarray([scale_lagrangian(multiplier*x,multiplier*v) for x,v in zip(lam,vel)])
    pairs=((1.2,3.4),(.7,5.2),(2.,math.sqrt(2)))
    isometry=max(abs(scale_distance(multiplier*x,multiplier*y)-scale_distance(x,y)) for x,y in pairs)
    log_transport=max(abs(scale_distance(x,y)-abs(math.log(x)-math.log(y))) for x,y in pairs)
    ladder=np.asarray([2.**n*a0 for n in range(steps+1)])
    ladder_step=max(abs(scale_distance(ladder[i+1],ladder[i])-math.log(2)) for i in range(steps))
    ladder_total=max(abs(scale_distance(x,a0)-n*math.log(2)) for n,x in enumerate(ladder))
    half=abs(scale_distance(math.sqrt(2),1)-.5*scale_distance(2,1))
    geodesic=max(abs(scale_distance(2.**r,2.**s)-abs(r-s)*math.log(2)) for r in rungs for s in rungs)
    horizon=energy*np.exp(-2*t); orbit=np.asarray([energy*dilation_flow(-2,float(x)) for x in t])
    proper=compton*math.log(schmidt)
    d={"group_error":group,"inverse_error":inverse,
       "lagrangian_error":float(np.max(abs(L-Lm))),
       "euler_lagrange_error":float(np.max(abs(acc*lam-vel**2))),
       "noether_charge_error":float(np.max(abs(vel/lam-generator))),
       "metric_isometry_error":isometry,"metric_log_error":log_transport,
       "ladder_step_error":ladder_step,"ladder_total_error":ladder_total,
       "sqrt_two_half_step_error":half,"geodesic_error":geodesic,
       "horizon_orbit_error":float(np.max(abs(horizon-orbit))),
       "schmidt_recovery_error":abs(math.exp(proper/compton)-schmidt),
       "gauss_fixed":all(abs(dilation_flow(0,float(x))-1)<1e-15 for x in t),
       "charged_sector_error":abs(scale_distance(dilation_flow(charge,charge_time),1)-abs(charge*charge_time))}
    return d
