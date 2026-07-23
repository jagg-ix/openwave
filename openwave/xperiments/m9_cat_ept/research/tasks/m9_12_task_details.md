# M9.12 task: three-dimensional representation and control qualification

## Goal

Establish a bounded four-component Dirac representation and independent free-spinor
and vacuum-Maxwell controls before enabling coupled three-dimensional transport.

## Representation

The standard Dirac matrices satisfy

```text
alpha_i^2 = beta^2 = I
{alpha_i,alpha_j} = 0, i != j
{alpha_i,beta} = 0.
```

## Free-spinor control

The free Hamiltonian is

```text
H_0 = alpha.( -i D ) + beta m.
```

The discrete centered-derivative symbol is evolved exactly in Fourier space and
compared with RK4 at `dt/dx={0.08,0.04,0.02}` on a `20^3` grid through `t=0.8`.

## Vacuum-Maxwell control

A right-moving periodic transverse wave is evolved without matter:

```text
A_y = 0.05 cos(x-t)
E_y = -0.05 sin(x-t).
```

The scored grid is `48x12x12`, `t=1.1`, with zero absorber.

## Acceptance

- all Clifford residuals at most `1e-14`;
- both free-time orders at least `3.5`;
- maximum free norm drift at most `3e-7`;
- vacuum `A` and `E` relative errors at most `2e-2`;
- vacuum field-energy drift at most `2e-5`.

## Selection transparency

The `3e-7` coarse free-norm threshold was fixed after an exploratory control run
showed fourth-order error with `2.57e-7` drift at the coarsest step. M9.12 is not
described as blind preregistration.

## Boundary

M9.12 validates representation and controls only. It does not establish coupled
three-dimensional Maxwell--Dirac transport or a particle solution.
