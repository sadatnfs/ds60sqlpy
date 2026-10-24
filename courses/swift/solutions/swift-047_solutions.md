# swift-047: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-047_solution.swift](swift-047_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep portable policy independent:** A portable core should not import a platform framework merely to format its basic domain outcome. The same domain summary works without a UI framework.

**Declare a capability rather than guess:** Capability descriptions should follow actual prepared runtime evidence. The Linux capability set does not invent SwiftUI support.

## Reason through the six tasks

1. **Predict and explain.** Identify which code belongs in the portable core.

2. **Guided modification.** Add a platform-neutral derived statistic.

3. **Independent construction.** Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.

4. **Diagnose a defect.** Diagnose importing UIKit in a shared domain target.

5. **Boundary evidence.** Test unavailable capabilities with a clear message rather than a broken Run action.

6. **Transfer and justify.** Create a platform support matrix listing compiled, executed and manually inspected surfaces separately.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Sharing Swift code does not mean every platform has the same frameworks or user expectations. A domain package can compile on Linux and Apple platforms, while UI adapters differ. Conditional compilation is useful at a narrow boundary; scattering platform checks throughout domain logic makes the core harder to reason about.

Deployment targets state the oldest platform APIs an app promises to support. Runtime availability checks can gate newer functionality, but the fallback must still be useful. Resource paths, permissions and application lifecycle also vary. Treat cross-platform support as a matrix of actual builds and runs, not a claim inferred from the language name.

#if canImport selects compile-time framework availability. #available guards runtime API availability on Apple platforms. Package platform declarations and Xcode deployment settings are related project contracts.

CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
