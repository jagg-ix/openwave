# M9.19 task: simulation-theory plugin contract

Replace acquisition-oriented infrastructure with a dimensionless theory manifest that every new theory must provide before shared OpenWave solvers can execute it.

Required declarations:

- dynamic, auxiliary, constraint, and ledger fields;
- bounded parameters and defaults;
- reversible, irreversible, source, and constraint evolution terms;
- observables and reductions;
- invariant, monotone, balance, and constraint laws;
- deterministic versioned serialization and fingerprinting.

The CAT/EPT reference manifest explicitly declares matter, gauge/geometry, entropy, reservoir, and constraint sectors. No physical-data acquisition interface is allowed.
