# M9.6 task: scalar-carrier charge, spin, and topology audit

## Question

Which particle attributes are genuinely represented by the current single complex
scalar field, and which require a replacement carrier?

## Required distinctions

The audit keeps separate:

1. global `U(1)` phase symmetry and conserved norm;
2. local `U(1)` gauge covariance and electric charge;
3. phase current and an opposite electric-charge sector;
4. intrinsic spatial rotation representation and spin;
5. model-specific topological protection.

## Frozen executable checks

1. global phase leaves density, norm, current, and scalar energy unchanged;
2. conjugation leaves norm and energy unchanged and reverses phase current;
3. a local phase leaves norm unchanged but changes ordinary-gradient energy when
   no gauge connection is present;
4. the localized profile has a continuous amplitude path `s psi`, `s in [0,1]`,
   to the zero vacuum;
5. the intrinsic scalar factor is `+1` after `2pi`, while the reference spinor is
   `-1` after `2pi` and returns after `4pi`;
6. no Maxwell source, Gauss-law flux, charge unit, spinor carrier, or declared
   topological target/boundary class exists in the current model;
7. the staged spinor replacement preserves the density interface through
   `Psi-dagger Psi = |psi|^2` for the embedding `Psi = (psi,0)`.

## Accepted conclusions

- positive: global `U(1)` norm symmetry is present;
- negative: conjugation is not an opposite electric-charge sector;
- negative: electric charge is not derived;
- negative: spin-1/2 is not represented;
- negative: the current profile has no protected topological sector because it
  contracts continuously to vacuum.

These conclusions apply to the current carrier and profile. They are not a theorem
that every scalar, gauge-coupled, or multi-component extension is impossible.

## Replacement routes

- locally gauge-coupled complex scalar: local covariance and charged spin-0 matter;
- Dirac/Weyl spinor plus local gauge coupling: spin-1/2 charge carrier;
- multi-component topological order parameter: possible winding and defect sectors.

Each route must preserve a positive density functional and the normalized-density
coarse-graining interface used by the entropic clock. None is claimed to localize
before a new numerical gate is run.
