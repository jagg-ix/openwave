# The M5 particle hunt: shapes measured, identifications hypothesized

The M5.20 and M5.21 series are one hunt with two topologies: a defect whose internal clock persists at contained energy. The SHAPE is what the simulations measure; the particle NAME is the hypothesis riding on it, so the "possibly" stays attached until the anchors land (framing agreed at the M5.21 close-out, 2026-07-14). M5.20's early tasks also built the shape-agnostic machinery both hunts run on (the 4×4 EOM, the analytic gap ladder, the clock census, the audited conservative-dynamics stack).

![the particle clock: the delta-axis sweeping about the director](images/clock.gif)

| Series | What is measured (the shape) | The identification hypothesis | What already supports it | What would firm it up |
| --- | --- | --- | --- | --- |
| [M5.20](m5_roadmap.md) (.1/.2/[.3](tasks/m5_20_3_task_details.md)) | A closed **VORTEX-LOOP** of the (δ,0) winding pair, half-integer, with a measured gap ladder and (so far) no unconstrained protection | Possibly the **neutrino** | The author's own ansatz language (his ellipse diagram, flavor-as-loop-state, the radius-breathing-during-oscillation remark); the M5.11 closed-loop → PMNS lineage; the near-zero rest-energy character of the winding pair | A constrained run where the loop persists, its radius breathes at conserved E_total, and the spectrum lands on the gap ladder (exactly M5.20.3's pre-registered observables) |
| [M5.21](tasks/m5_21_task_details.md) (.1/.2) | A radial **HEDGEHOG** charge defect, 3-equal-melting core, intrinsic core-breathing clock, topological charge that survives everything thrown at it | Possibly the **electron** | The M5.11 Faber electron (511 keV) lineage; the M5.16 parameter-free r_half = 2.926 fm; charge-1 winding robustness measured at M5.21 | A constrained run where the energy is contained and the clock persists (M5.21.1), then the quantum-number checks (spin / magnetic-moment channels already in the panel catalog) |

The asymmetry: the electron identification already has quantitative anchors (511 keV, r_half), while the neutrino identification is still structural (right topology, right ansatz, right oscillation story, no calibrated number yet). So "possibly the electron" is currently the stronger "possibly", and M5.20.3's breathing spectrum is the neutrino side's first shot at a number.

![the lepton family as axis choices of the biaxial spectrum](images/leptons.png)

**The identification question went public (2026-07-14)**: the author convened Marc, Andras, and Giorgio on models-of-particles ("Fable is now able to model vortex loop - maybe let's try to verify if it is rather electron or neutrino?"), offering to help if convinced the loop is the electron, and naming a discriminator: replace the Lagrangian and try to get Coulomb, as required for an electron ([`tasks/m5_20_convo.md`](tasks/m5_20_convo.md) message 3). This page's tables are the internal scorecard for exactly that debate; note the two camps put DIFFERENT shapes behind "electron" (their vortex loop vs this page's hedgehog), so the discriminating observables (Coulomb tail, 511 keV anchor, charge quantization, oscillation phenomenology) matter more than the shape vocabulary.

## The Duda-criteria scorecard (2026-07-14): which shape is the electron?

Scored against the criteria the author himself laid out (Coulomb as the named discriminator; angular momentum propelled by the negative Hamiltonian terms), using only what the simulations have already measured:

| Duda's criterion | Hedgehog (the M5.21 object) | Vortex loop as-simulated (the M5.20 object) |
| --- | --- | --- |
| **Coulomb, "as required for electron"** (his named discriminator) | ✅ measured: the far-field curvature energy density is exactly 8c₂/r⁴ (the M5.16 G3/G4 anchors), which is the Coulomb form (E ~ 1/r² gives energy ~ 1/r⁴); quantitatively anchored: c₂ = αħc/64π with α⁻¹ → 137 measured (M5.11, the Faber anchor) | ❌ nothing: the (δ,0)-pair winding has no monopole flux; its far field is localized/dipole-like, no 1/r⁴ tail in any run |
| Charge quantization | ✅ integer π₂ degree; q = 1.000 measured at every radius through the entire M5.21 noclock evolution | The pair winding is a different (chargeless) class; its q is a winding along the loop, not a monopole charge |
| Mass anchor | ✅ 511 keV calibration (M5.11 Faber electron) + parameter-free r_half = 2.926 fm (M5.16) | Near-zero rest-energy character, which is exactly why it fits the NEUTRINO |
| Angular momentum / spin ("negative terms propel electron angular momentum") | 🚧 untested under the true L: the canonical-stack kick stalled (M5.21); this is precisely M5.21.1 | 🚧 same, M5.20.3 |
| Stability | ⚠️ slides (Q8) in unconstrained stacks | ⚠️ unwinds 10/10 in unconstrained stacks: a neutral criterion until the true-L runs |

Three quantitative electron anchors sit on the hedgehog side (the Coulomb-form tail, α⁻¹ → 137, 511 keV + r_half) versus zero on the as-simulated loop side, and the loop's near-zero-mass character actively argues neutrino.

**The synthesis nuance (worth holding; our own data produced it)**: in LC topology a point hedgehog and a small charged disclination ring live in the SAME topological sector: a hedgehog can open into a ring carrying the identical monopole charge. M5.16's Q8 measured exactly that tendency (the point form is a saddle; the melt moves off-origin, toward a ring-like core). So Marc/Andras/Giorgio's "electron = vortex loop" and our "electron = hedgehog" may be two core-regimes of the same charged object. The sharp discriminator is then not loop-vs-point shape at all, it is the WINDING CLASS: monopole-charged (Coulomb tail, our hedgehog/charged-ring) = electron; the chargeless (δ,0) pair loop (no Coulomb, near-zero energy, flavor-oscillation-friendly) = neutrino, which is Duda's loop and the one M5.20 simulates. Under that reading, both camps can be right about "loop" while Duda stays right about which loop is the neutrino.

**The shared missing ingredient (measured, not a hunch)**: containment is exactly what the constraint must buy. In the unconstrained canonical stack the defect's energy is not contained (the statics is a saddle-slide; a kinetic clock kick radiates), while the topological charge and the core-breathing clock survive ([M5.21 findings](findings/m5_21_films.md)). [M5.20.3](tasks/m5_20_3_task_details.md) lands the constraint on the loop; M5.21.1 puts it on the electron and reruns the identical clock-vs-noclock comparison against the M5.21 baseline. If the constrained clock contains the energy where the unconstrained kick radiated, that is "the particle clock creating particle stability" on film.
