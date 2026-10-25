# Restartable File Pipelines and Honest Durability Guarantees

**Stable ID:** `python-pro-03`

**Estimated time:** 270 minutes, split across sessions as needed.

## Level and prerequisites

Advanced. Direct catalog prerequisites: `python-23`, `python-10`.

You can process records in batches, work with files and JSON, and test failure behavior. This lab adds restart semantics and local publication boundaries using only the standard library. One writer owns each checkpoint. It does not introduce distributed coordination or promise power-loss durability on every filesystem.

## Learning objectives

- Pin exact source bytes before processing and reject a changed source on resume.
- Store progress and aggregate results together behind one atomic publication boundary.
- Deduplicate replayed identities while rejecting conflicting duplicates.
- Inject a failure before replacement, resume, and compare with a clean run.
- Separate process-restart correctness from concurrency and power-loss guarantees.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional contributor route:** use the prepared environment in
[CONTRIBUTING](../../../CONTRIBUTING.md) on Linux, macOS or Windows through
WSL 2. The commands below assume its packages are already installed. They are
not prerequisites for opening this lesson in the Docker classroom. Local
`.learning/` files and CLI progress belong to this checkout; they do not read or
update the Docker classroom's named learning volume.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_pro_03_restartable_file_pipeline.py). Copy it to an ignored
folder under `.learning/` first if you want to keep your attempt across course
updates. Use the interpreter from setup. These examples need only Python's
standard library, have no network calls, and use the same inputs on each run.

Prepared POSIX/WSL contributor terminal:

```sh
uv run --no-sync python python/professional/lessons/py_pro_03_restartable_file_pipeline.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_pro_03_restartable_file_pipeline_solutions.md) and
[runnable solution](../solutions/py_pro_03_restartable_file_pipeline_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

A pipeline can crash after doing work but before recording that it finished.
On restart, it must know which input and committed result belong together.
Treat the checkpoint as a sealed receipt containing both progress and the
result at that progress. If the receipt and result lived in independent files,
replacing one successfully would not make the pair an atomic transaction.
This lab keeps them in the same JSON document and replaces that one file.

- **Checkpoint:** persisted progress plus enough state to resume the declared
  computation from an inspected boundary.
- **Snapshot identity:** a hash of the exact source bytes used by this run,
  including encoding and line endings.
- **Replay:** processing an input again after uncertain or repeated delivery.
- **Idempotency:** repeating an operation with the same identity and content
  has the same externally visible result as performing it once.
- **Atomic replacement:** a successful name replacement exposes a complete
  old or complete new file rather than a partially rewritten target.
- **Durability:** survival of committed state across a stated failure model;
  process failure and power loss are different models.

The input is UTF-8 JSON Lines: one JSON object per nonempty physical line.
Blank lines and duplicate JSON field names are rejected so offset counting
and field meaning remain explicit. Each record
contains exactly `id` and `quantity`. Id is nonempty trimmed text; quantity is
a nonnegative integer, excluding bool. Repeating an id with the same quantity
is an idempotent replay. Repeating it with a different quantity is a conflict
and rejects the whole snapshot before publication. A correction needs an
explicit version or event identity; last-write-wins is not silently assumed.

The checkpoint contains version, source SHA-256, source byte size, next row,
unique quantities by id, total quantity, and completion status. Next row is
the number of source records already accounted for, including identical
replays. The unique count and total only count each identity once. State is
recomputed for the committed prefix when loading, catching invalid progress,
unexpected keys, or inconsistent totals rather than trusting arbitrary JSON.

## Worked example / walkthrough

### Example A: keep related state in one publication

```python
state = {"next_row": 3, "quantities": {"A": 2, "B": 5}, "total_quantity": 7, "complete": False}
assert state["next_row"] == 3
assert sum(state["quantities"].values()) == state["total_quantity"]
```

Expected observation: three processed source rows can represent two unique
identities when one row was a replay. The mapping and total travel with the
offset. Publishing an offset of three while retaining a total from only one
record would be inconsistent. JSON is just a format; putting values in JSON
does not automatically validate or transactionally coordinate several files.

### Example B: inspect exact input identity

```python
import hashlib

first = b'{"id":"A","quantity":2}\n'
same_meaning_new_bytes = b'{"id": "A", "quantity": 2}\n'
assert hashlib.sha256(first).hexdigest() != hashlib.sha256(same_meaning_new_bytes).hexdigest()
```

Expected observation: spacing changes the byte hash even though the parsed
record has the same meaning. This lab pins byte identity deliberately so a
resume cannot quietly reinterpret a different source. A semantic content
hash is another legitimate design, but needs canonicalization and its own
versioned contract. SHA-256 detects content differences; without a trusted
signature or key it does not prove who created the source.

### Replacement sequence and its limits

Create a temporary file in the target directory so replacement stays on the
same filesystem. Write complete UTF-8 JSON, flush Python's buffer, fsync the
file, close it, then call `os.replace`. Closing before replacement is important
for Windows file-handle behavior. Remove only the temporary file created by
this attempt when an exception occurs. Preserve the old checkpoint and every
learner-owned file. A test hook raises before replacement so a test can
observe that the old published checkpoint is unchanged.

This sequence prevents partial target contents for the stated single-writer
process-restart model. It does not establish directory-entry persistence after
sudden power loss on every platform, nor protect against concurrent writers,
network filesystem behavior, disk failure, or malicious state modification.
File fsync and atomic rename solve different parts of the problem. State
those limits beside the evidence instead of calling the design universally
crash-proof or exactly-once.

### Replay without pretending work executes once

Each committed batch publishes a new prefix state. If the next candidate
fails before replacement, the old prefix remains authoritative and the next
run can repeat uncommitted computation. Because the aggregate derives from
source identities and committed prefix together, replay does not double-count
the result. The computation may execute more than once. That differs from a
claim that each instruction or external side effect happens exactly once.

The reference re-derives state from a small source prefix for transparent
validation. That is intentionally simple and can do repeated work across many
batches. Measure and redesign for large sources only after preserving the
same state invariants. This lab also validates the entire snapshot before the
first write, so it is a bounded-file design rather than an unbounded streaming
reader. It demonstrates restart reasoning, not a universal high-throughput
ingestion engine.

## Exercises

1. **Pin and validate a snapshot.** Implement `read_snapshot` returning source bytes and validated records. Require exact id/quantity keys and reject blank lines, malformed JSON, wrong types, and negative quantities.

   **Verify:** A valid two-record file returns two rows and its exact bytes; `true` as quantity, a blank line, or an extra field raises ValueError before state publication.

   **Hint:** In Python bool is an int subclass, so an integer-only check needs an explicit bool exclusion.

2. **Declare replay and conflict behavior.** Test A/2, A/2, B/5 versus A/2, A/3. Reject a conflicting identity before publishing any prefix.

   **Verify:** Identical replays produce unique count 2 and total 7 after three source rows; the conflict snapshot raises ValueError and creates no checkpoint.

   **Hint:** Identity equality and content equality are both required for an idempotent replay.

3. **Derive inspectable prefix state.** Implement `state_for_prefix` with version, hash, byte size, next_row, quantities, total, and completion. Validate the offset and preserve exact accounting.

   **Verify:** For A/2, A/2, B/5 at next_row 2, total is 2, unique count is 1, and complete is False; at 3, total is 7 and complete is True.

   **Hint:** The offset counts source rows; the aggregate counts unique ids.

4. **Publish one complete state.** Implement `atomic_write_state` with a same-directory temporary file, flush/fsync, close, and replace. Add a before_replace test hook.

   **Verify:** A failure injected before replacement leaves the prior target bytes unchanged and no temporary file from that attempt. A successful replacement parses as complete JSON.

   **Hint:** A temp file plus a target file is safe only when the target name changes after the temp is complete.

5. **Resume after a failed candidate.** Implement `run_pipeline` with batch_size 2. Use five unique records and inject failure before committing offset 4, then resume without failure.

   **Verify:** After failure, committed next_row remains 2; after resume it is 5, complete is True, and total matches a clean run with no double counting.

   **Hint:** Resume from the published prefix, not from the last value a local variable reached.

6. **Reject stale or corrupt state.** Resume after changing source bytes, then separately tamper the saved total or next_row. Preserve the original evidence in temporary copies.

   **Verify:** Changed source hash, invalid offset, and inconsistent prefix total each raise ValueError; none silently resets or overwrites the checkpoint.

   **Hint:** A valid JSON file can still violate the checkpoint contract.

7. **Prove repeat and empty behavior.** Run a completed source again and compare checkpoint bytes. Then process a new empty source with a separate checkpoint and test invalid batch sizes.

   **Verify:** A completed rerun leaves bytes unchanged; empty input commits a complete zero-row/zero-total state; zero, negative, and bool batch sizes raise ValueError.

   **Hint:** Check idempotent external state separately from how many times internal code executes.

8. **Write an honest guarantee.** Write a short runbook containing source identity, one-writer ownership, retry command, state inspection fields, failure test, and filesystem limits.

   **Verify:** The runbook artifact includes the checkpoint path, source hash, inspected next_row after failure, and one-file publication policy. Its guarantee table marks multi-writer and power-loss durability as unverified.

   **Hint:** Do not promote a process-interruption test into evidence for every failure model.

## Self-check

Explain the inconsistent state a two-file offset/result design can expose.
Trace failure before and after replacement. Describe why exact input bytes
are pinned and why identical hash is not an authenticity proof. Distinguish
one committed result from exactly one execution of every internal operation.

## Common pitfalls

If totals double after retry, inspect replay identity and the committed prefix.
If a changed source resumes, check the hash before processing. If Windows
replacement fails, inspect open temporary/target handles before changing
paths. If state parses but results disagree, re-derive its prefix and compare
all fields. If tests remove every nearby temp file, narrow cleanup to the one
path owned by this attempt so learner work is preserved.

## Next step

Study database transactions and idempotency in the bridge track, where several
records can share a real transaction boundary. Before adding concurrent writers
or external side effects, define ownership, conflict detection, and the exact
failure model rather than reusing this single-writer file design unchanged.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for python-pro-03.
Read python/professional/companion-guides/py_pro_03_restartable_file_pipeline.md and python/professional/lessons/py_pro_03_restartable_file_pipeline.py.
Check my direct prerequisites: python-23, python-10.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```
