# M9.38 finding: manifest-to-accelerator contract closes

The reference manifest compiles to five aligned buffers totaling `2624` bytes.
The flat-buffer accelerator emulator and NumPy reference agree exactly for
matter, metric, entropy, reservoir, and observable buffers. Matter-plus-reservoir
balance closes to machine precision. Generated source and plan fingerprints are
deterministic, and malformed states and unsupported IR are rejected.

No hardware GPU runtime was executed. Focused validation: `8 passed`.
