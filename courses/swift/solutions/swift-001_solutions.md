# swift-001: explanation and comparison

Reference program: [swift-001_solution.swift](swift-001_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Check before printing:** The check establishes a specific observation before the program claims completion. Hello, Swift appears before the lesson marker.

**Compute an observable result:** The second condition rejects the plausible mistake of adding dimensions instead of multiplying them. The computed seat count is 24.

## Task answers

### Task 1: Predict and explain

Predict the greeting count before execution.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let greeting = "Hello, Swift"
let letters = "Hello".count + "Swift".count
precondition(letters == 10)
precondition(greeting.count == letters + 2)
```

**Observe:** Hello, Swift has 12 Characters: 10 letters plus the comma and the space.

Counting the two words separately and adding the punctuation by hand gives a prediction that does not come from greeting.count itself, so the check can disagree with it.

### Task 2: Guided modification

Change the greeting and independently recount its characters.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let greeting = "Good morning"
let words = greeting.split(separator: " ")
precondition(words.map(\.count) == [4, 7])
precondition(greeting.count == 4 + 1 + 7)
```

**Observe:** Good morning splits into words of 4 and 7 Characters, and the whole greeting counts 12 with the space.

The recount is built from the parts (two words and one separator), so changing the greeting text without recounting makes the final precondition fail instead of passing silently.

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

**Written answer.** Deleting the brace that closes `static func main()` makes swiftc stop with a diagnostic such as `expected '}' in struct` pointing at the end of main.swift. That is a compilation failure: no program was produced, so Hello, Swift, the preconditions and the swift-001 marker never run. Record that first diagnostic, restore the brace, and confirm the marker returns; a failed precondition would instead report a file and line after execution had started.

### Task 5: Boundary evidence

Check zero shelves and one shelf.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let booksPerShelf = 8
func capacity(shelves: Int) -> Int { shelves * booksPerShelf }
precondition(capacity(shelves: 0) == 0)
precondition(capacity(shelves: 1) == 8)
precondition(capacity(shelves: 1) != 1 + booksPerShelf)
```

**Observe:** Zero shelves hold 0 books and one shelf holds 8, not the 9 that adding the dimensions would give.

Zero is the identity edge of the multiplication and one shelf isolates the per-shelf amount, so the two cases catch a wrong operator that the three-shelf case alone could hide.

### Task 6: Transfer and justify

Model a three-level capacity calculation and explain every intermediate value.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** The reference places three independent scenarios inside one `@main` type: the greeting check, the rows-by-seats product and the task 3 shelf capacity. Each scenario computes a value, states the expected number with `precondition`, and only then lets control reach the final `print` of the lesson marker.

**Why it is correct.** The string "Hello, Swift" has five letters, a comma, a space and five more letters, so its count is 12. Four rows of six seats is 24, and three shelves of eight books is also 24. Because every check runs before the marker, the marker can only appear when all three numbers match.

**A plausible wrong approach.** A tempting shortcut is to compute `rows + seatsPerRow`, which gives 10 and still looks like a plausible capacity. The second precondition in Example B exists to reject exactly that answer. Another mistake is deleting a failing precondition so the marker prints; the program then claims completion without evidence.

**How to verify.** Compile and run the reference in the `swift-linux` pad. Expect `Hello, Swift` on the first line and the marker last. Then temporarily change `seatsPerRow` to 5 and confirm the process stops at the seat check, which proves the check is live rather than decorative.

## Mechanism and diagnostic reasoning

Swift is a compiled language used for portable tools and for applications built with platform frameworks. The language, its standard library and Apple user-interface frameworks are separate layers. A Linux Swift compiler can execute language and portable Foundation code. It does not provide SwiftUI or an iPhone simulator.

The classroom stages one main.swift file and compiles it in Swift 6 mode. An explicit @main type tells the compiler where execution begins. The wrapper uses an asynchronous throwing main so later lessons can keep the same shape. For now, statements execute in order. A compiler error means the program never reached main; a failed precondition means execution reached a violated assumption.

`@main` marks the entrypoint type. `struct LessonMain` names that type. `static func main() async throws` declares its entry method; async and throws are explained in later chapters. `let` binds a value that cannot be reassigned. `print` produces visible output.

Do not delete a failed precondition to reach the marker. Preserve the first compiler diagnostic before interpreting later errors. The entrypoint wrapper is required by this classroom compile contract.

## Review before continuing

Run the reference and confirm it prints `swift-001: passed`, then rerun the guide's counterexample.
