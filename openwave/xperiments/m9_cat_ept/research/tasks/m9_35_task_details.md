# M9.35 task: multi-domain coupling scheduler

Compile manifest-declared read/write relations into deterministic execution
stages. Support explicit lagged feedback, transactional stage updates,
provenance traces, and rejection of unknown fields, cycles, and multiple writers.

The scheduler validates execution structure, not physical correctness.
