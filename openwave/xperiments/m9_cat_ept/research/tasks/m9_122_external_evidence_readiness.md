# M9.122 preregistered gates

## M9.122a package

- preserve the M9.121 prediction commitment;
- verify artifact and package SHA-256 digests;
- require commitment timestamp before evidence reveal;
- reject anchor use of target observables;
- require complete held-out observations and uncertainties;
- keep the live template incomplete.

## M9.122b evaluator

- return `blocked` for an incomplete or tampered package;
- compute physical rates only from an independently supplied positive time scale;
- evaluate both target sectors against a fixed z-score threshold;
- permit synthetic fixtures to test code paths but never to promote external validation.

## M9.122c identity

- reject label-only identity;
- require independent source, model transition ID, observed channel, four discriminator classes, and negative controls;
- reject self-asserted bridges;
- keep physical identity false until a real external-observation artifact is ingested.
