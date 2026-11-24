# swift-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-009_solution.swift](swift-009_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate an independent array value:** The language contract concerns observable behavior even if storage was initially shared. Appending to the copy leaves the original unchanged.

**Do not confuse capacity and count:** Capacity is a performance hint, not an index range. Reserving twenty slots creates no logical elements.

## Task answers

### Task 1: Predict and explain

Predict original and changed arrays after append.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let original = [1, 2]
var changed = original
changed.append(3)
precondition(original == [1, 2] && original.count == 2)
precondition(changed == [1, 2, 3] && changed.count == 3)
```

**Observe:** original stays [1, 2] with count 2, while changed becomes [1, 2, 3] with count 3.

Assigning an array copies the value; the shared buffer is duplicated only when changed is first mutated, so the append never reaches original.

### Task 2: Guided modification

Replace an element in the copy and retain the original.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let original = [1, 2, 3]
var copy = original
copy[0] = 10
precondition(copy == [10, 2, 3])
precondition(original == [1, 2, 3])
```

**Observe:** Replacing the first element of the copy gives [10, 2, 3] and original keeps [1, 2, 3].

Subscript assignment is a mutation like append, so copy-on-write gives copy its own storage before element 0 changes.

### Task 3: Independent construction

Build a filtered array without changing the source.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let source = [-1, 2, -3, 4]
let positives = source.filter { $0 > 0 }
precondition(positives == [2, 4])
precondition(source == [-1, 2, -3, 4])
```

**Observe:** The filtered array is [2, 4] and the source is unchanged.

filter returns a new array; because arrays are values, the source keeps its own elements.

### Task 4: Diagnose a defect

Diagnose indexing a reserved but still empty array.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
var values: [Int] = []
values.reserveCapacity(20)
precondition(values.capacity >= 20 && values.isEmpty)
precondition(!values.indices.contains(0))
values.append(7)
precondition(values.indices.contains(0) && values[0] == 7)
```

**Observe:** After reserving 20 slots, index 0 is still not valid; it becomes valid only after appending 7.

Valid indices come from count, not capacity, so values[0] on the reserved but empty array would trap with Index out of range. Checking indices.contains(0) shows the difference without crashing.

### Task 5: Boundary evidence

Test an empty slice and a slice whose startIndex is not zero.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let values = [10, 20, 30, 40]
let empty = values[2..<2]
precondition(empty.isEmpty && empty.startIndex == 2)
let tail = values[1...]
precondition(tail.startIndex == 1 && tail.first == 20)
precondition(tail[tail.startIndex] == 20 && tail[1] == 20)
```

**Observe:** The empty slice 2..<2 starts at index 2, and the tail slice starts at index 1 where it reads 20.

An ArraySlice shares its base array's indices, so tail[0] would trap; reading through startIndex or first works for any slice.

### Task 6: Transfer and justify

Explain what changes when array elements are mutable class instances.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Build a filtered array without changing the source) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A copies `[1, 2]` into a `var`, appends 3 to the copy, and checks both arrays. Example B reserves capacity for 20 elements in an empty array and then appends one value. The task 3 answer builds a filtered array of even values without touching the source.

**Why it is correct.** Arrays are values, so after `changed.append(3)` the original still equals `[1, 2]` even if storage was shared until the write. `reserveCapacity(20)` only allocates room: `count` stays 0 until the append, after which index 0 holds 7. `filter` returns a new array, so the task 3 result is `[2, 4]` and the source keeps its elements.

**A plausible wrong approach.** After `reserveCapacity(20)`, writing `values[0] = 7` looks reasonable because space exists, but the array has no element at index 0 and the access traps. Assuming an `ArraySlice` starts at 0 fails in a similar way: a slice of indices 2 through 3 has `startIndex == 2`.

**How to verify.** Print `values.capacity` and `values.count` after the reserve in a scratch pad; capacity is at least 20 and count is 0. For task 5, check that `Array([5, 6, 7, 8][2...]).first == 7` while the slice's `startIndex` is 2.

## Mechanism and diagnostic reasoning

Swift arrays are value types. Assigning an array produces a value that behaves independently when later mutated. The implementation can share backing storage until a write requires separation, a strategy called copy-on-write. The semantic promise is independent values, not a guarantee that every assignment immediately copies all bytes.

An array of class references still contains references as its element values. Copying the array separates its sequence structure but does not clone every referenced object. Keep that distinction in mind when building snapshots or undo history. Capacity is storage preparation and does not change the count of present elements.

`[Int]` is an array type. append grows logical count; an index replaces an existing element. reserveCapacity prepares storage. ArraySlice may preserve original indices, so use its indices rather than assuming zero.

Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.

## Review before continuing

Run the reference and confirm that it prints `swift-009: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
