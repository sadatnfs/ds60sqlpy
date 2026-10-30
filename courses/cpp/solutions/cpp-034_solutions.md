# cpp-034: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Data layout determines which values are adjacent in memory. Array-of-structs stores complete records together; struct-of-arrays groups each field separately. Locality can reduce memory traffic when a calculation uses one field, while another workload may favor complete records. Allocation count is a separate cost from algorithmic work.

## Detailed reasoning

Physical grouping should follow the access pattern being measured. Summing only values may benefit from keeping those values together, while a routine consuming full records may prefer another layout. The reference proves that both forms still represent the same three values and sum to 60. reserve changes capacity, not size, so writing through index zero after reserve alone is invalid. Populate elements through push_back or resize before accessing them.

<!-- depth:start -->
## Data layout follows the access pattern

An array of structures stores complete records together. A structure-of-arrays layout stores each field in its own sequence. Neither layout is universally faster. The useful question is which fields the operation reads and in what order. Summing only value can benefit from dense values, while operations that need id and value together may favor a record layout.

The first example stores three Sample records with IDs1, 2, 3 and values 10, 20, 30. It visits each record and adds value. The second stores just the values and uses accumulation. Both must produce60 before any timing comparison is meaningful. Equal totals are a basic correctness check; in a richer transformation, also verify that identity-to-value relationships remain intact.

reserve(rows.size()) can avoid repeated growth allocations while materializing a values vector. It changes capacity, not size. push_back constructs the actual elements. Writing values[0] immediately after reserve on an empty vector would violate the element-access contract. This is a concrete link between performance-oriented allocation control and the ownership rules from cpp-007.

Data movement has a cost. Creating a separate values sequence may improve repeated scans but require an upfront copy and additional memory. If only one tiny scan is performed, the conversion cost can dominate. A benchmark should state whether layout conversion is included and how many queries reuse the result. Otherwise two timings can describe different amounts of work.

Hardware cache behavior, alignment, compiler vectorization and input size influence performance. The tiny fixture teaches representation and equality of results, not a cache-speed claim. Measure a representative bounded workload in the intended build configuration, and keep the original data contract visible while changing layout.

## Debugging the contract

If a layout optimization changes which value belongs to an ID, the transformation is wrong even when the total happens to match. If reserve appears to create elements, inspect size separately. If a benchmark excludes conversion for one layout but includes it for another, state that asymmetry before comparing. If a tiny fixture shows unstable timing, do not extrapolate a production speedup from it.
<!-- depth:end -->

## Worked example 1

```cpp
std::vector<Sample> rows{{1, 10}, {2, 20}, {3, 30}};
```

Expected: Three full records retain the relationship between identity and value.

## Worked example 2

```cpp
std::vector<int> values{10, 20, 30};
assert(std::accumulate(values.begin(), values.end(), 0) == 60);
```

Expected: The value-only representation yields the same total 60.

## Exercise 1: Draw both layouts

Sketch three records as AoS and as separate ID/value vectors.

**Expected:** Same three logical rows with different physical grouping.

**Reasoning:** Representation must preserve the row relationship.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Prove result equality

Sum values in both representations.

**Expected:** 60 from each.

**Reasoning:** Correctness is checked before performance.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Inspect reserve

Reserve 100 on an empty vector, then inspect size.

**Expected:** Size 0; capacity at least 100.

**Reasoning:** Reserved storage is not constructed logical elements.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair an unfair comparison

One candidate omits the value 30.

**Expected:** Reject timing comparison until both checksums equal 60.

**Reasoning:** Doing less work can falsely look faster.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Measure bounded work

Repeat one-field summation with a fixed row cap and build mode.

**Expected:** Same checksum, duration units and repetitions recorded.

**Reasoning:** Layout benefits depend on access pattern and hardware.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer the workload

Now request ID and value together for every row.

**Expected:** Reassess the locality hypothesis without assuming SoA always wins.

**Reasoning:** The useful representation follows the query pattern.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
