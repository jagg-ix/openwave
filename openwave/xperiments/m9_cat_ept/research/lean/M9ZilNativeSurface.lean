import Zil.Native

/-!
# M9.98 ZIL native-root smoke fixture

`Zil.Native` is the explicit root for standalone facts, theorem-shaped rules,
queries, provenance, workflow, authorization, and audit tooling.  OpenWave `.zc`
programs are assigned to this runtime surface.

Do not import the PhysLib-facing `Zil` Datalog root in this module.  The roots
are built as separate public targets by current `zil-lean`.
-/

#check Zil.Term
#check Zil.Rule
#check Zil.Query
#check Zil.Program

example : True := by trivial
