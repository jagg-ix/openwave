# M9.20 task: reversible/irreversible evolution engine

Provide a reusable operator-splitting engine for theories whose evolution separates into reversible and irreversible sectors.

The reference kernel evolves a complex state with a Hermitian Hamiltonian and positive loss operator. The engine must:

- support Lie and Strang splitting;
- keep the two generators explicit;
- transfer lost norm into a reservoir ledger;
- derive a monotone entropic clock;
- close extended matter-plus-reservoir balance;
- reduce to unitary evolution when the irreversible generator vanishes;
- demonstrate second-order Strang convergence for noncommuting generators.
