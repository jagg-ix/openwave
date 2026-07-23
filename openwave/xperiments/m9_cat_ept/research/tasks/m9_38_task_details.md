# M9.38 task: manifest-driven accelerator adapter

Lower a versioned theory manifest into aligned flat buffers, deterministic field
views, a validated kernel IR, generated accelerator source, and reference/device
parity checks. Reject unsupported operations, malformed shapes, and implicit
write hazards.

Hardware GPU execution and speedup are separate qualification targets.
