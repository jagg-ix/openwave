# M9.21 finding: theory comparison is reproducible and law-aware

The shared scenario evaluates a reversible control and two irreversible CAT/EPT-style rate members on the same 51-point timeline. All declared laws pass, deterministic replay hashes match, and every pairwise trajectory distance is nonzero.

The rate sweep orders the final matter norm correctly and the finite-difference parameter sensitivity is nonzero. The harness therefore supports regression, falsification, and comparative simulation without introducing experimental-data assumptions.

Focused validation: `8 passed`; combined simulation-core suite: `24 passed`. No CI workflow was run or inspected.
