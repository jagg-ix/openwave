# M9.20 task: noisy open-set discrimination benchmark

## Question

Can the three selected back-reaction interfaces be distinguished under controlled
synthetic noise, and which reduced observable sets remain structurally ambiguous?

## Frozen benchmark

- observables: accessible trace, normalized purity, reservoir transfer;
- 21 times on `[0,5]`;
- Gaussian noise `sigma=0.015`;
- 241-point rate grid on `[0.05,0.35]`;
- alternating train/held-out time indices;
- 40 trials per mechanism;
- explicit out-of-family rejection threshold.

## Gates

- full-panel accuracy at least 95%;
- every held-out winning margin positive;
- trace-only amplitude/reservoir ambiguity exposed exactly;
- out-of-family signature rejected;
- no physical mechanism selected from synthetic data.
