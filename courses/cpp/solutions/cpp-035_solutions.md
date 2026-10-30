# cpp-035: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Algorithmic complexity describes how work grows as input grows. A representation can change that work: repeated linear search differs from building an index once. A benchmark compares defined workloads under measured conditions. For tiny collections, index setup may outweigh faster lookup, so asymptotic reasoning and actual budgets both matter.

## Detailed reasoning

Index building has an upfront cost that can be repaid across repeated queries. A map count preserves both occurrences of key 2; a set would answer a different question. The seemingly read-like counts[9] inserts a missing key with zero, whereas find does not change the map. That behavioral difference can contaminate an experiment and the data contract. Report index construction separately from lookup work and keep the queried answers identical.

<!-- depth:start -->
## Algorithmic work and index side effects

Complexity describes how work grows with input size under a stated model. A linear scan visits elements to answer a query. An index spends work and memory building a reusable structure so later queries can be cheaper. The right choice depends on the number of queries, update frequency, key distribution and required semantics, not only a big-O label.

The map fixture counts occurrences of 2, 3, 2, 4. The count for2 is 2, which preserves multiplicity. A set would retain only membership and answer a different question. The index construction traverses every input and updates counts. That upfront work must be included when comparing one query with a direct scan, and can be amortized only when the index is actually reused.

map::find is an observation that does not insert a missing key. operator[] can insert a value-initialized mapped value when the key is absent. The second complete program demonstrates this difference:find(9) leaves size unchanged, while counts[9] creates a new zero entry. A read-like expression can therefore mutate the data and distort later measurements or reports.

Ordering is also part of the container contract. std::map maintains an ordering by its comparator, whereas unordered alternatives have different iteration and performance properties. Do not rely on unspecified order when emitting a deterministic report. If output order matters, choose or impose it deliberately rather than inheriting it accidentally from one implementation run.

A useful performance comparison checks identical answers first, then records index build cost, lookup count and memory tradeoffs. It includes missing keys and repeated keys because they exercise different paths. A faster method that drops duplicate events or inserts new data during lookup does not satisfy the original contract.

## Debugging the contract

If a map grows during a supposedly read-only report, search for operator[] on missing keys. If duplicates disappear, check whether a set replaced a count map. If two approaches give different answers, resolve semantics before timing. If an index helps only after many queries, report the build cost and reuse threshold instead of presenting lookup-only timing as the total task cost.
<!-- depth:end -->

## Worked example 1

```cpp
for (int x : std::vector<int>{2, 3, 2, 4})
  ++counts[x];
```

Expected: The index holds 2->2, 3->1, 4->1.

## Worked example 2

```cpp
assert(counts.find(9) == counts.end());
```

Expected: A non-mutating lookup reports absence without inserting key 9.

## Exercise 1: Count linear work

Search four rows for key 2 once.

**Expected:** Four comparisons and count 2.

**Reasoning:** A scan inspects every element for a complete count.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Build an index

Build frequency map for [2, 3, 2, 4].

**Expected:** Three keys with counts 2, 1, 1.

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
