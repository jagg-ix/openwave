# M9.7c task: transverse Maxwell--spinor radiation qualification

## Question

Can M9 leave spherical electrostatics and demonstrate a bounded transverse gauge
mode with magnetic energy, nonzero-capable Poynting flux, dynamic Gauss closure,
absorbing boundaries, emitted-energy accounting, and a genuine spinor-current
back-reaction interface?

## Scope split

M9.7c is divided into three scored milestones:

1. **M9.7c1 -- vacuum transverse Maxwell benchmark**
   - propagate an exact right-moving pulse;
   - verify second-order convergence and field-energy conservation.
2. **M9.7c2 -- neutral spinor-current coupling**
   - evolve a charge-conjugate local spinor pair;
   - couple its transverse current to `A_y` in both directions;
   - preserve zero signed charge and Gauss law without projection.
3. **M9.7c3 -- radiation and absorber ledger**
   - measure nonzero Poynting flux through interior probes;
   - absorb outgoing radiation with a conductivity layer;
   - close field, matter, absorbed, and emitted-energy ledgers;
   - verify window and absorber-parameter stability.

## Frozen bounded model

The transverse gauge field depends on one Cartesian coordinate:

```text
A = A_y(x,t)
E = E_y = -A_t
B = B_z = A_x
A_t = -E
E_t = -A_xx - J - sigma(x) E.
```

Two local two-component spinors carry opposite dimensionless charges:

```text
i psi_s,t = [m sigma_z - s q A sigma_y] psi_s
s in {+1,-1}
J = q psi_+^dagger sigma_y psi_+
    - q psi_-^dagger sigma_y psi_-.
```

The initial pointwise densities are equal, so

```text
rho_q = q(|psi_+|^2-|psi_-|^2) = 0.
```

Symmetric local spinor evolution preserves this cancellation. The transverse Gauss
constraint therefore closes dynamically without a Poisson projection.

## Frozen parameters

```text
m = 1
q = 0.35
polarization angle = 0.45
envelope width = 2.5
total matter norm = 1
gauge seed amplitude = 0.01
gauge seed width = 4.
```

The spinor pair is a neutral radiating polarization source. It is not a charged
single-particle solution.

## Numerical method

- periodic second-order spatial differences;
- explicit fourth-order Runge--Kutta time integration;
- conductivity absorber near both edges;
- field energy `1/2 integral(E^2+B^2) dx`;
- matter energy from the instantaneous local Dirac Hamiltonian;
- absorbed energy `integral sigma E^2 dx dt`;
- emitted energy from outward Poynting flux through symmetric probes.

The corrected balance is

```text
E_matter + E_field + E_absorbed = constant
```

up to numerical truncation.

## Frozen studies

### Vacuum refinement

```text
L = 60
t = 12
points = {256,512,1024}
dt = 0.2 dx
absorber disabled.
```

### Coupled refinement

```text
L = 60
t = 18
points = {256,512,1024}
dt = 0.18 dx
absorber fraction = 0.20
absorber strength = 0.45.
```

### Long run

```text
L = 60
points = 1024
t = 80.
```

### Absorber/window study

```text
L in {50,60,70}
fixed dx approximately 0.1171875
t = 75
absorber fraction in {0.18,0.20,0.22}
absorber strength in {0.40,0.45,0.50}.
```

## Frozen acceptance

- all vacuum pulse orders at least `1.7`;
- coupled `A` and `E` self-convergence orders at least `1.5`;
- maximum signed charge density at most `2e-12`;
- pointwise pair-norm mismatch at most `2e-12`;
- finest corrected-energy drift at most `2e-4`;
- emitted energy at least `1e-5`;
- long-run absorbed energy at least `1e-5`;
- long-run corrected-energy drift at most `3e-4`;
- emitted-energy absorber-study spread at most `20%`;
- at least `25%` of final field energy outside the central matter region.

## Scope boundary

Passing M9.7c establishes a bounded transverse Maxwell radiation sector with
spinor-current back-reaction. It does not establish a full spatial
Maxwell--Dirac PDE, a localized charged particle, electron identity, fermionic
quantization, or three-dimensional non-spherical orbital stability.
