# cpp-041: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A release packet connects source identity to a tested binary and a documented platform. Portability is demonstrated by execution on each claimed environment. Reproducibility records enough inputs to repeat a build, while performance evidence states workload, limits and measurements. A release checklist must keep untested platforms visible.

## Detailed reasoning

A release packet should let another reviewer connect source, build configuration, executable and test observations. Keep Debug/Release results separate because NDEBUG and optimization change behavior and observability. The same checksum must hold before comparing performance. An untested platform stays unqualified even when a build file mentions it. Rollback needs an identifiable compatible artifact and a check that shows the restored version still meets its input/output contract.

<!-- depth:start -->
## A release packet connects source to behavior

A release is an identifiable artifact with an explicit contract and evidence for supported environments. A version string alone does not connect the binary to the source, compiler options or tested fixture. Record source revision or hash, toolchain, architecture, build configuration, dependency identities and the output schema that consumers rely on.

The example report uses schema 1, rows3, total6. Its always-active condition checks the checksum before printing the report. This matters in Release builds where ordinary assert expressions may be removed. A successful build followed by an unchecked output string could otherwise look like acceptance even if the actual computation changed.

Debug and optimized builds answer related but different questions. Debug information helps diagnosis; optimization changes performance and can expose latent undefined behavior. Both should preserve the declared result. Keep timing observations separate from correctness assertions, and record the exact flags used. A configuration name by itself is not enough to reproduce a binary.

A platform matrix should contain actual tested rows and explicit unavailable rows. Mentioning Windows, macOS and Linux in a build file does not qualify all of them. A Linux container binary also has a specific CPU architecture and cannot be assumed to run natively on every host that can display the guide. Runtime environment and packaging are part of the handoff.

Rollback needs a known compatible artifact and a check that the restored version satisfies the expected input/output contract. Reusing an old executable accidentally after a failed build is not a controlled rollback. Keep artifact identity and the decision explicit. If data format changed between versions, rollback may require compatibility handling beyond switching a binary.

## Debugging the contract

If a release test passes only in Debug, inspect assert-only validation and configuration-dependent behavior. If a report claims a schema version but its fields changed, fix versioning and consumer tests. If the wrong artifact runs, record the executable path and hash instead of trusting its filename. If a platform was not exercised, mark it unqualified rather than copying another platform's result into the matrix.
<!-- depth:end -->

## Worked example 1

```cpp
if (std::accumulate(fixture.begin(), fixture.end(), 0) != 6)
  return 1;
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

**Expected:** Both report rows=3, total=6 and actual executed test count.

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
