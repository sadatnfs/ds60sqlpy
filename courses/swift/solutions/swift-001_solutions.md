# swift-001: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-001_solution.swift](swift-001_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check before printing:** The check establishes a specific observation before the program claims completion. Hello, Swift appears before the lesson marker.

**Compute an observable result:** The second condition rejects the plausible mistake of adding dimensions instead of multiplying them. The computed seat count is 24.

## Task answers

### Task 1: Predict and explain

Predict the greeting count before execution.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The check establishes a specific observation before the program claims completion. Hello, Swift appears before the lesson marker.

### Task 2: Guided modification

Change the greeting and independently recount its characters.

No separate reference answer has been written for this task. Start from Example B: The second condition rejects the plausible mistake of adding dimensions instead of multiplying them. The computed seat count is 24.

### Task 3: Independent construction

Compute the capacity of three shelves holding eight books each.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let shelves = 3
let booksPerShelf = 8
let capacity = shelves * booksPerShelf
precondition(capacity == 24)
```

**Observe:** Three shelves of eight books hold 24 books.

The product is written as a calculation, and the precondition compares it with 24, a value worked out independently.

### Task 4: Diagnose a defect

Remove a closing brace temporarily and classify the failure as compilation.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Do not delete a failed precondition to reach the marker. Preserve the first compiler diagnostic before interpreting later errors. The entrypoint wrapper is required by this classroom compile contract.

### Task 5: Boundary evidence

Check zero shelves and one shelf.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Check before printing) and Example B (Compute an observable result).

### Task 6: Transfer and justify

Model a three-level capacity calculation and explain every intermediate value.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Source**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Swift is a compiled language used for portable tools and for applications built with platform frameworks. The language, its standard library and Apple user-interface frameworks are separate layers. A Linux Swift compiler can execute language and portable Foundation code. It does not provide SwiftUI or an iPhone simulator.

The classroom stages one main.swift file and compiles it in Swift 6 mode. An explicit @main type tells the compiler where execution begins. The wrapper uses an asynchronous throwing main so later lessons can keep the same shape. For now, statements execute in order. A compiler error means the program never reached main; a failed precondition means execution reached a violated assumption.

`@main` marks the entrypoint type. `struct LessonMain` names that type. `static func main() async throws` declares its entry method; async and throws are explained in later chapters. `let` binds a value that cannot be reassigned. `print` produces visible output.

Do not delete a failed precondition to reach the marker. Preserve the first compiler diagnostic before interpreting later errors. The entrypoint wrapper is required by this classroom compile contract.

## Review before continuing

Run the reference and confirm that it prints `swift-001: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
