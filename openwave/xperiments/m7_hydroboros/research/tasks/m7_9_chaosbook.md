# M7.9: ChaosBook study + canonical-exercise benchmark

> **Status: BACKLOG** (opened at the 2026-07-06 Phase-1-review call; Phase 1 extension). Roadmap row: [`m7_roadmap.md`](../m7_roadmap.md). Author-convo record: `theory/author_convos/m7_phase1_convo.pdf` (local-only). This doc carries the plan; FINDINGS land here at FINISH.

## 1. Objective

Two outputs, one task: (a) a **benchmark suite** the author can trust: canonical exercises from Cvitanović et al., *Chaos: Classical and Quantum* ("ChaosBook", <https://chaosbook.org/>), implemented headless and checked against their published solutions ("your AI should kill it in 10 minutes, **but I want to see that**"); (b) the **orbit-hunting toolkit** (Poincaré sections, return maps, periodic-orbit finding, cycle stability) that the reserved M7.10-M7.14 pure-Maxwell/Beltrami track will need. A side output: light reading support so Rodrigo gains call fluency without becoming the bottleneck.

## 2. Why (from the call)

The author's program is to find the electron as a **stable periodic orbit** in the electromagnetic field flow ("islands of superstability", the solar-system analogy), and ChaosBook is his named "Bible" for that methodology. The benchmark doubles as the self-test he asked for: proof that what comes out of this platform is computed, not "linguistically mirrored", on problems with known answers. Follow-ups agreed at the call ride this task: 4-7 walkthrough sessions on the book, a test-design review session with **Burak Budan**, and possibly a later look by **Cvitanović** himself.

## 3. Context-window strategy (the book is ~1000 pages; NEVER load it whole)

| Rule | How |
| --- | --- |
| Use the chapter structure, not the tome | chaosbook.org serves the webbook **per chapter**; the author also sent a copy (persist to `theory/` per the corpus rules + a `_CITATIONS.md` entry). Build a local **index file first** (TOC → chapter → topics → exercises), then load only the chapter section + exercise statement relevant to the step in hand |
| Target chapters only | the working set is small: the overture (ch. 1), flows, maps + return maps, **Poincaré sections**, fixed points + how to find them (Newton / multiple shooting), **cycle stability** (Floquet), plus the worked examples attached to those chapters. Everything else is out of scope for this task |
| Per-exercise loading | one exercise at a time: statement + the minimal supporting section; solutions compared at the END (implement first, check after, so the known answer never leaks into the implementation) |

## 4. Plan

| Step | Content |
| --- | --- |
| E1 acquire + index | persist the book copy (local, gitignored, citation entry); build `m7_9_chaosbook_index.md` (chapter map + candidate exercises) |
| E2 select | 3-5 canonical exercises **with published solutions**, spanning the toolkit: e.g. Rössler / Lorenz equilibria + their stability eigenvalues, a Poincaré-section construction, the shortest periodic orbits of a canonical flow (Rössler cycle or Hénon map cycles) found by Newton / multiple shooting, cycle counting on a symbolic-dynamics example (3-disk pinball class) |
| E3 implement | headless Python (`scripts/m7_9_chaosbook_*.py`), unit tests asserting the published values; implement-first-check-after per E-loading rule; the integrator layer reuses our own machinery where that is the point (drift behavior on chaotic flows is itself evidence for walkthrough § 3) |
| E4 benchmark report | a short method-note-lite report (equations, code links, our numbers vs the book's, pass/fail table) suitable for the author and the Burak review |
| E5 reading support | a 2-page "what you need for the calls" digest for Rodrigo (TOC orientation + ch. 1 + the vocabulary: Poincaré section, return map, Floquet multiplier, cycle expansion), explicitly bounded: fluency, not mastery |
| E6 sessions | schedule the 4-7 book walkthrough sessions + the Burak test-design hour AFTER E4 exists (the report is the shared artifact to walk through) |

## 5. Effort estimate + independence from Rodrigo's reading

**The benchmark (E1-E4) does not wait for anyone's reading.** The exercises are small ODE / map systems (three variables, not `N³` fields): compute time is seconds, and the real effort is fidelity to the book's definitions plus the honest compare. Estimate: **E1-E4 in one to two focused sessions** (a normal task run each, the first ending at the E2 selection checkpoint if the cap intervenes), E5 half a session more. Rodrigo's 2-3 weeks of light reading (the author's own suggested dose: "TOC + dabbling your feet in the first chapter... you don't need to go super deep to be mega efficient") runs in parallel and gates nothing here; it only gates how interactive the E6 sessions can be, which is exactly where his time is best spent given M5, M7, and the DHC build phase all compete for it.

## 6. Cross-refs

[Roadmap](../m7_roadmap.md) · [M7.8](m7_8_helicity_pair.md) (the walkthrough this benchmark reinforces) · the reserved M7.10-M7.14 Maxwell-track band (the consumer of the toolkit) · [tracker Q4](../m7_question_tracker.md#q4-detail) (source-material provenance) · corpus anchor for the chaotic-flow direction: Dombre et al. 1986 (ABC chaotic streamlines, [`theory/_CITATIONS.md`](../../theory/_CITATIONS.md)).
