# rust-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-023_solution.rs](rust-023_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Call a reviewed public function:** The implementation details remain behind its named boundary. The consumer uses the domain module interface.

**Import a name without changing ownership:** Use changes name resolution, not execution or data ownership. The shorter imported name refers to the same function.

## Reason through the six tasks

1. **Predict and explain.** Identify the public and private items.

2. **Guided modification.** Add a private helper used by the public function.

3. **Independent construction.** Move a pure domain operation into an inline module.

4. **Diagnose a defect.** Diagnose a consumer accessing a private representation field.

5. **Boundary evidence.** Test the public contract without relying on internal helper names.

6. **Transfer and justify.** Split a future library and executable crate by responsibility and document dependency direction.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Modules organize names and control visibility. A private implementation can change without forcing every consumer to understand it. Public items form a compatibility boundary and should expose domain meaning rather than internal representation. A crate is a compilation unit; a package can contain a library crate and executable crates.

The classroom can demonstrate modules inside one source file. A real multi-file Cargo project has separate preparation and is not uploaded through the pad. Keep that distinction explicit when a lesson introduces src/lib.rs and integration tests. Good module boundaries follow responsibilities and dependency direction, not a fixed rule that every type needs its own file.

`mod domain { ... }` declares a module. pub exposes an item to permitted external paths. use imports a name into scope without copying its implementation. pub(crate) limits visibility to the current crate.

Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
