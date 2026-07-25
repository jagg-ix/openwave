import Zil

/-!
# M9.98 ZIL Datalog-root smoke fixture

`Zil` is intentionally the PhysLib-facing clause-logic root.  It provides the
Datalog compatibility API used by embedded formalization metadata, including
attachments, theorem intents, file contracts, tactics, and `Holds` semantics.

Do not import `Zil.Native` in this module.  Keeping the roots in separate smoke
fixtures makes accidental root-role collapse visible during an external Lean
build.
-/

#check Zil.Datalog.Program
#check Zil.Program
#check Zil.Holds
#check Zil.Datalog.declarationAttachments
#check Zil.Datalog.fileContracts
#check Zil.Datalog.theoremIntents

example : True := by trivial
