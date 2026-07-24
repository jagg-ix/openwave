# M9.55 task: kernel-checked evidence refresh

Refresh the exact PhysLib/ZIL source and declaration snapshot using a fail-closed promotion policy. A formal promotion requires a matching Git blob, a declared witness, explicit `kernel_checked` state, and no open assumptions. Exercise stale-source, missing-witness, and open-assumption rejection controls. Record zero promotions when the inspected continuum generator stack remains `pending_ci`, interface-only, or open.
