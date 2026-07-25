# M9.97 task details

## Objective

Extend M9.96 from static source/field consistency to one self-consistent gauge-spinor stationary campaign and one full Maxwell--Dirac pair/control evolution. Measure momentum transfer, center acceleration, and spin response without promoting physical criteria unless all shared branch and calibration gates close.

## M9.97a -- gauge-spinor stationary feasibility

- Embed the field-derived winding-three candidate into a two-component Pauli spinor.
- Use the selected cubic--quintic density action.
- Replace the ordinary kinetic term by a gauge-covariant spectral kinetic term.
- Recompute charge, current, scalar potential, vector potential, electric field, and magnetic field at every imaginary-time step.
- Include the tree-level Pauli coupling with `g = 2`.
- Measure normalization, winding, spin, radius, boundary loading, Maxwell constraints, and full stationary residual.
- Preserve spin one-half under a measured finite-iteration tolerance.
- A passing state must satisfy every gate on the same field.
- If no state passes, record the negative subresult and promote nothing.

## M9.97b -- Maxwell--Dirac momentum and center response

- Construct opposite field-derived winding candidates on one periodic lattice.
- Use Pauli fields only to seed positive-energy four-spinor embeddings.
- Regenerate charge, Dirac current, Maxwell fields, and Lorentz force from the actual four-spinors.
- Initialize the bounded Maxwell--Dirac engine from those four-spinor-generated fields.
- Evolve a matched one-source self-field control using the same positive four-spinor.
- Subtract the control response from the pair response.
- Compare interaction-induced kinetic-momentum transfer with the external Lorentz-volume force.
- Fit interaction-induced center acceleration independently.
- Record the center sign and magnitude without assuming they agree with momentum transfer.
- Preserve norm, integrated charge, pair neutrality, and field-source boundaries.

## M9.97c -- full-generator and BMT spin response

- Initialize transverse spin so partner magnetic fields generate a measurable precession.
- Measure the finite-time spin rate from the evolved four-spinor.
- Compute the instantaneous spin derivative from the exact Dirac generator used by the PDE.
- Use the shortest four-sample fit window to limit finite-time curvature.
- Require finite-time and generator rates to agree within the preregistered tolerance.
- Compare the same response with the imported rest-frame Dirac--Pauli/T-BMT rate.
- Treat a rest-frame mismatch as a failed reduction, not a numerical integration failure.
- Do not infer covariant Thomas/BMT dynamics from the rest-frame theorem.

## M9.97 formal overlay

Pin and import:

- `ThomasBMTMagicCancellation.lean`;
- `EMParticleDynamics.lean`;
- `PointParticle/ThreeDimension.lean`.

Fail closed on missing or changed blobs. Retain the formal boundaries for the covariant boost/Thomas extension and loop computation of `F2`.

## Acceptance summary

```text
stationary winding and spin preserved                required; spin error <= 2e-7
stationary residual below gate                       tested, may fail honestly
Maxwell constraints                                  required
four-spinor integrated charges                       +1 and -1 within 2e-12
momentum transfer versus Lorentz force               relative error <= 0.10
center acceleration sign and magnitude               measured independently
finite-time spin versus exact generator              relative error <= 0.03
finite-time spin versus rest-frame BMT               measured independently
criterion promotion                                   forbidden while blockers remain
```

## Status policy

M9.97 may close dimensionless subreductions without promoting a criterion. Magnetic moment/spin, electric force, and magnetic force remain partial while any of the following are absent:

- a stable charged spinorial stationary branch;
- converged center acceleration with the Lorentz-force sign;
- a derived covariant moving-packet spin law;
- common physical calibration;
- withheld external predictions.
