# cpp-041: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A release packet connects source identity to a tested binary and a documented platform. Portability is demonstrated by execution on each claimed environment. Reproducibility records enough inputs to repeat a build, while performance evidence states workload, limits and measurements. A release checklist must keep untested platforms visible.

## Worked example 1

```cpp
if(std::accumulate(fixture.begin(),fixture.end(),0)!=6) return 1;
```

Expected: The release check remains active even under NDEBUG.

## Worked example 2

```cpp
std::cout << "schema=1 rows=3 total=6\n";
```

Expected: The result names a schema version, input count and exact checksum.

## Exercise 1: Inventory the release

Record source revision or content hashes plus compiler/architecture.

**Expected:** All identities present without machine-specific source paths.

**Reasoning:** The packet must identify what was actually built.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Compare build modes

Run always-active checks in Debug and Release host builds.

**Expected:** Both report rows=3,total=6 and actual executed test count.

**Reasoning:** NDEBUG must not remove the only checks.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Bound a benchmark

Declare row count, repeats and output checksum before timing.

**Expected:** Units, variability and same-work evidence retained.

**Reasoning:** Performance evidence needs correctness and workload identity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair platform claims

Review a packet tested only on arm64 Linux but claiming Windows.

**Expected:** Windows remains unqualified until actual execution.

**Reasoning:** A build configuration is not a platform receipt.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check offline replay

Rebuild in a fresh owned directory using prepared dependencies.

**Expected:** No network access needed and tests reproduce.

**Reasoning:** Missing dependencies are a reproducibility failure to report.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer rollback

Keep a previous known-good binary and compatible input contract.

**Expected:** A reviewer can identify rollback artifact and acceptance test.

**Reasoning:** Rollback requires a usable artifact, not just a written promise.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
