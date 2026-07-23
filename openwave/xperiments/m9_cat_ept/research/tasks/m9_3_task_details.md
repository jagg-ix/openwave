# M9.3 task: fixed probability map and coarse-graining clocks

## Frozen question

Can M9 construct an explicit information-loss ledger from a wave-function
snapshot without declaring unitary simulation time itself irreversible?

## Field-to-probability map

For the 512-cell M9.2 lattice, freeze

```text
p_i = dx |psi_i|^2 / sum_j dx |psi_j|^2.
```

No phase, current, adaptive partition, fitted bins, or density threshold enters
the map.

## Frozen channel

Use the periodic nearest-neighbor Markov channel

```text
(Kp)_i = 1/4 p_{i-1} + 1/2 p_i + 1/4 p_{i+1}.
```

The channel is doubly stochastic, preserves the uniform distribution, and is
applied for exactly 64 depths. The calibration is fixed at `gamma = 1`.

## Distinct observables

Do not use one entropy name for three different quantities:

1. `I(X;Y)` for the one-step joint `p(x) K(y|x)`;
2. remaining disequilibrium `D(p_n || u)`;
3. accumulated gain `D(p_0 || u) - D(p_n || u)`.

The second decreases under the fixed channel. The third increases and is the
appropriate accumulated coarse-graining clock. The first is a nonnegative
correlation observable and is not assumed monotone.

## Inputs

Run the map independently on the initial and final snapshots of the frozen M9.2
Gaussian benchmark. This compares two unitary states; channel depth remains a
separate parameter.

## Acceptance

- probabilities remain normalized and nonnegative;
- the uniform distribution is fixed;
- remaining disequilibrium is nonincreasing at every depth;
- accumulated gain is nondecreasing and positive by depth 64;
- every one-step total correlation is nonnegative;
- `D_0 = D_n + gain_n` closes within `1e-12`;
- all conclusions hold for both snapshots.

## Nonclaims

A pass does not establish monotonicity in physical time, a unique physical
coarse-graining, irreversible back-reaction, or particle localization.
