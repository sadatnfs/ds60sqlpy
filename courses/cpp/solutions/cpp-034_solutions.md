# cpp-034: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Data layout determines which values are adjacent in memory. Array-of-structs stores complete records together; struct-of-arrays groups each field separately. Locality can reduce memory traffic when a calculation uses one field, while another workload may favor complete records. Allocation count is a separate cost from algorithmic work.

## Detailed reasoning

Physical grouping should follow the access pattern being measured. Summing only values may benefit from keeping those values together, while a routine consuming full records may prefer another layout. The reference proves that both forms still represent the same three values and sum to 60. reserve changes capacity, not size, so writing through index zero after reserve alone is invalid. Populate elements through push_back or resize before accessing them.

## Worked example 1

```cpp
std::vector<Sample> rows{{1,10},{2,20},{3,30}};
```

Expected: Three full records retain the relationship between identity and value.

## Worked example 2

```cpp
std::vector<int> values{10,20,30}; assert(std::accumulate(values.begin(),values.end(),0)==60);
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
