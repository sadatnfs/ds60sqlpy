# cpp-035: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Algorithmic complexity describes how work grows as input grows. A representation can change that work: repeated linear search differs from building an index once. A benchmark compares defined workloads under measured conditions. For tiny collections, index setup may outweigh faster lookup, so asymptotic reasoning and actual budgets both matter.

## Worked example 1

```cpp
for(int x:std::vector<int>{2,3,2,4}) ++counts[x];
```

Expected: The index holds 2->2, 3->1, 4->1.

## Worked example 2

```cpp
assert(counts.find(9)==counts.end());
```

Expected: A non-mutating lookup reports absence without inserting key 9.

## Exercise 1: Count linear work

Search four rows for key 2 once.

**Expected:** Four comparisons and count 2.

**Reasoning:** A scan inspects every element for a complete count.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Build an index

Build frequency map for [2,3,2,4].

**Expected:** Three keys with counts 2,1,1.

**Reasoning:** The representation preserves duplicate multiplicity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Compare repeated queries

Compare 100 full scans with one index build plus 100 lookups.

**Expected:** Same answers; setup and lookup work reported separately.

**Reasoning:** Amortization depends on number of queries.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair mutating lookup

Use counts[9] to inspect absence, then repair with find.

**Expected:** operator[] inserts zero; find leaves key count unchanged.

**Reasoning:** Read syntax can mutate a map.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check empty data

Build and query an empty frequency index.

**Expected:** No key 2 and zero matching rows.

**Reasoning:** Avoid accidental insertion during an absence check.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer sorted storage

Compare binary search on a sorted vector with map lookup.

**Expected:** Sorting cost, duplicate range and lookup budget documented.

**Reasoning:** The best choice depends on updates and query frequency.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
