# swift-010: explanation and comparison

Reference program: [swift-010_solution.swift](swift-010_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Preserve absence and zero:** Optional lookup prevents missing information from being confused with a stored value. Pear is present with zero and apple is absent.

**Deduplicate and order deliberately:** Set semantics establish uniqueness while sorting separately establishes order. Duplicate red is not inserted and sorted output is deterministic.

## Task answers

### Task 1: Predict and explain

Explain the optional result of each dictionary lookup.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let counts = ["pear": 0]
let pear: Int? = counts["pear"]
let apple: Int? = counts["apple"]
precondition(pear == .some(0))
precondition(apple == .none)
precondition(counts["apple", default: 0] == 0)
```

**Observe:** Looking up pear gives .some(0), apple gives .none, and only the default subscript turns apple into 0.

A lookup returns Int? because the key may be missing; the optional keeps a stored zero apart from absence until the caller deliberately supplies a default.

### Task 2: Guided modification

Count repeated tags using the default-value subscript.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let tags = ["red", "blue", "red", "red"]
var counts: [String: Int] = [:]
for tag in tags { counts[tag, default: 0] += 1 }
precondition(counts == ["red": 3, "blue": 1])
```

**Observe:** Counting the four tags gives red: 3 and blue: 1.

counts[tag, default: 0] reads 0 for a new tag and the += writes the incremented value back, inserting the key on its first occurrence.

### Task 3: Independent construction

Build a unique sorted list of accepted inventory names.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let rows = ["pear", "apple", "pear", "", "fig"]
let names = Set(rows.filter { !$0.isEmpty }).sorted()
precondition(names == ["apple", "fig", "pear"])
```

**Observe:** The accepted names are apple, fig and pear, each once and sorted.

Empty names are rejected first, the Set removes duplicates, and sorted() gives a stable order that does not depend on hashing.

### Task 4: Diagnose a defect

Diagnose persisting hashValue as a cross-run identifier.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct Product: Hashable {
  let sku: String
}
let product = Product(sku: "A-17")
let storedKey = product.sku
precondition(Product(sku: storedKey) == product)
precondition(product.hashValue == Product(sku: "A-17").hashValue)
```

**Observe:** The stored SKU A-17 rebuilds an equal Product; hashValue matches only between values inside this same run.

Swift seeds hashing randomly per process, so a hashValue written to disk will not match in the next run. Persist the stable field (the SKU) and let Hashable compute hashes in memory.

### Task 5: Boundary evidence

Test missing, present-zero and duplicate keys.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
var stock = ["pear": 0]
precondition(stock["kiwi"] == nil && stock["pear"] == 0)
stock["pear"] = 5
precondition(stock.count == 1 && stock["pear"] == 5)
let merged = Dictionary([("fig", 1), ("fig", 2)], uniquingKeysWith: +)
precondition(merged == ["fig": 3])
```

**Observe:** kiwi is missing, pear is present at 0 and then replaced by 5 without a second entry, and duplicate fig pairs merge to 3.

Assigning to an existing key replaces its value, and Dictionary(_:uniquingKeysWith:) makes the duplicate-key policy explicit instead of trapping.

### Task 6: Transfer and justify

Design a custom Hashable key using only stable identity fields.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A stores pear with a count of zero and reads both pear and the missing apple through the dictionary subscript, which returns `Int?`. Example B inserts into a `Set<String>` and reads the `inserted` flag, then sorts for a stable order. The task 3 answer builds a unique sorted list of accepted inventory names.

**Why it is correct.** `counts["pear"]` is `.some(0)` and `counts["apple"]` is nil, so absence and a stored zero stay distinct. Inserting red a second time returns `inserted == false` because sets keep one copy per equal element. Sorting turns the unordered set into `["blue", "red"]`, a deterministic report order.

**A plausible wrong approach.** Iterating the set directly and expecting `["red", "blue"]` because that was the insertion order is a common error; Swift sets and dictionaries have no order contract, and the order can change between runs. Persisting `hashValue` as an identifier fails for the same reason, because hashing is seeded per process.

**How to verify.** The task 3 output is apple, fig and pear, each once and sorted. For task 2, use `tally[tag, default: 0] += 1` over a list with red twice and confirm red maps to 2 while an unseen key still reads as nil.

## Mechanism and diagnostic reasoning

A Dictionary associates unique keys with values; a Set stores unique members. Both use Hashable to narrow equality lookup. Equal values must hash consistently. A hash value is not a persistent identifier and should not be saved as an enduring key, since hashing can vary across process runs.

Dictionary lookup returns an optional, preserving the distinction between a missing key and a present zero. Output order is not a business sorting policy. Sort keys explicitly for stable presentation. When designing a custom key, use stable identity fields and avoid changing a key after it has been inserted into hashed storage.

`[String: Int]` declares a dictionary. `counts[key, default: 0] += 1` inserts a default only for that mutation. Set.insert returns whether an element was newly inserted. sorted establishes presentation order.

Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.

## Review before continuing

Run the reference and confirm it prints `swift-010: passed`, then rerun the guide's counterexample.
