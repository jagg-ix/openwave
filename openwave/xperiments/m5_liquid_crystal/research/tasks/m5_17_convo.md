# M5.17 convo record (Duda ↔ Rodrigo)

> The message exchange attached to task [M5.17](m5_17_task_details.md); datestamped entries accumulate in chronological order (the per-task convo convention, adopted 2026-07-05: one `m5_<id>_convo.md` per task that exchanges messages; some tasks have none, some accumulate several). Lineage: follows [`m5_4i_convo_2026.07.04.md`](m5_4i_convo_2026.07.04.md) (group threads) and [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md) (the audit failure that created the method-note standard; last of the retired date-keyed `m5_4x` naming).

## 2026-07-05: Duda's first reply to the method note (audit PASS + the 4D spec)

Duda's 2026-07-05 01:03 reply to the M5.17 re-ask email (method note + two-charge Coulomb run + Q13/Q14/Q15).

### 1. The reply in brief

"Thanks, looks better." He quotes the functional VERBATIM from [`../findings/m5_17_methods_note.md`](../findings/m5_17_methods_note.md) (E[M], u_curv, V(M_sp)) and confirms it: "This is 3D, (a,b,c) should be chosen to have minimum for eigenspectrum (1,delta,0)." Then the new content: "For 4D, required to add clock and gravity, potential needs to have minimum (g,1,delta,0), also this commutator needs to include signature in 4D: [A,B] = A xi B - B xi A for xi = diag(-1,1,1,1)." Closes with "Will study further and write."

### 2. What it settles

| # | Item | Consequence + routing |
| --- | --- | --- |
| 1 | **The method-note standard WORKS**: he found the Hamiltonian and potential in one click and quoted them back verbatim (contrast 2026-07-03: "still I have no idea what does it calculate") | The audit failure is closed; METHOD NOTE (`dev_docs/METHOD_NOTE.md`) is validated as the owner-facing format. No further legibility work needed on M5.16/M5.17 |
| 2 | **First owner sign-off on the exact static functional**: the E[M] we locked `c2 = alpha*hbar*c/(64 pi)` on is now owner-confirmed | The M5.16 Coulomb lock and the M5.17 two-charge cross-check sit on an owner-signed-off energy; upgrade their standing in any scorecard |
| 3 | **NO retroactive change to M5.16/M5.17 numbers** (verified, not assumed): the signature commutator reduces identically to the plain commutator on our static fields, because `M[0,0] = g` is uniform and the time-space mixing is zero everywhere, so every `dM` has a zero time block (`hedgehog_field`, `curvature_density_np` in [`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py)) | Lock, `r_half`, two-charge curve, melt-channel finding all stand. M5.16 gate G8 (g-blindness) is now owner-endorsed as a feature of the static sector |
| 4 | **NEW 4D SPEC (a): potential minimum `(g, 1, delta, 0)`** for the clock + gravity extension | Pre-condition for any dynamic/4D run: extend V from `M_sp` to the full 4x4 M with enough independent invariants to pin 4 distinct eigenvalues (generically Tr M through Tr M^4). The paper p.11 anchor hints (`g^4 ~ ke^2/Gm^2 ~ 1e38`, `delta^2 ~ hbar*c`) become COEFFICIENT CONSTRAINTS on that potential. Routed: [`m5_12_task_details.md`](m5_12_task_details.md) phase-D spec + Q17 detail ([`../m5_question_tracker.md`](../m5_question_tracker.md)) |
| 5 | **NEW 4D SPEC (b): signature commutator `[A,B]_xi = A xi B - B xi A`, `xi = diag(-1,1,1,1)`** in the curvature term | Mandatory the moment time derivatives or time-mixing textures enter (the psi clock dynamics). The module's convention block already declares `eta = diag(-1,1,1,1)`; only the kernel needs the xi insertion when we go dynamic. Routed: M5.12 phase-D spec |
| 6 | **Q15 nuance**: he EXPECTS the vacuum spectrum `(1, delta, 0)`, genuinely biaxial; a quartic trace LdG cannot have a strict minimum there (exactly Q15's territory), and the 4D `(g,1,delta,0)` minimum needs still more invariants | Does NOT answer Q15, but makes a "yes, higher invariants" answer structurally likely and extends Q15's scope from the 3D vacuum to the 4D one. Routed: Q15 detail |

### 3. What stays pending

Q13 (chiral Lifshitz + Frank), Q14 (what holds the hedgehog / the pairs), Q15 (sixth-order pinning): "Will study further and write." No reply needed from our side; the next inbound is his.

### Cross-links

- The note he audited: [`../findings/m5_17_methods_note.md`](../findings/m5_17_methods_note.md) (gains a § 10 addendum pointing here)
- Consumer of items 4-5: [`m5_12_task_details.md`](m5_12_task_details.md) § 2026-07-05 spec update (phase D)
- Consumer of items 4, 6: [`../m5_question_tracker.md`](../m5_question_tracker.md) Q15 + Q17 details
- Predecessor exchanges: [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md), [`m5_4i_convo_2026.07.04.md`](m5_4i_convo_2026.07.04.md)
