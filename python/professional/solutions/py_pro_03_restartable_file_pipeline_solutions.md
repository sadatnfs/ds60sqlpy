# Restartable File Pipelines and Honest Durability Guarantees: solution reasoning

Stable ID: `python-pro-03`.

Read the [guide](../companion-guides/py_pro_03_restartable_file_pipeline.md) and attempt the [learner artifact](../lessons/py_pro_03_restartable_file_pipeline.py) first. The [executable solution](py_pro_03_restartable_file_pipeline_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The checkpoint is also the published result. That single-file
boundary is the central design choice. A temporary candidate can be discarded
without changing the old state. A completed state can be read repeatedly
without rewriting it. Source identity and a re-derived prefix make resumption
explicit instead of treating any parseable JSON as trusted progress.

```python
quantities = {"A": 2, "B": 5}
assert len(quantities) == 2
assert sum(quantities.values()) == 7
```

The reference intentionally reads a bounded snapshot and validates all rows
before committing progress. It uses one writer, small deterministic data, and
same-directory replacement. Its failure injection tests a process boundary,
not a physical power loss. Never run this demonstration against another
learner's state or remove files you did not create.

## Exercise 1. Pin and validate a snapshot

Read bytes once, decode as UTF-8, and parse each physical line as one JSON object. The exact key set, trimmed nonempty text id, and nonnegative integer quantity form a small inspectable schema. Booleans are rejected despite Python considering bool an int subclass. Blank lines are rejected so a source-row offset has one unambiguous meaning. Parsing the whole snapshot before publication means an invalid suffix cannot leave a partially accepted source. This trades streaming scale for transparent teaching behavior and should be stated as a bounded-file assumption.

## Exercise 2. Declare replay and conflict behavior

Track the first quantity for each id while validating the snapshot. A repeated equal quantity is an idempotent replay and does not add units again. A differing quantity is a conflict that requires a source correction or explicit version policy. Reject it before creating or replacing a checkpoint. Three source rows A/2, A/2, B/5 therefore represent two unique identities and seven units. This does not prove the original quantities are true, nor does it make an external side effect idempotent merely because the in-memory sum is.

## Exercise 3. Derive inspectable prefix state

A prefix state counts every processed source row in next_row, including replays. Its unique mapping and sum represent the accepted identities in that prefix. At offset two in the replay example, only A contributes and total is two; after the third row B contributes five and total is seven. Completion means offset equals source row count. Validate offset type and range so a negative value cannot invoke Python's slice-from-end behavior. The persisted source hash and byte size identify exactly which snapshot the offset belongs to.

## Exercise 4. Publish one complete state

Write the full candidate into a temporary file in the target directory, flush buffered text, fsync the underlying file, close it, and then replace the target name. Injecting an error before replace demonstrates that old target bytes remain authoritative. Clean up only the candidate path created in this attempt, including on exceptions. Closing before replace avoids a common Windows handle problem. These steps do not prove parent-directory persistence after sudden power loss on every filesystem; document that boundary instead of calling the implementation unconditionally durable.

## Exercise 5. Resume after a failed candidate

With batches of two, the first committed state has offset two. The next candidate reaches offset four in memory, but the injected pre-replace error prevents publication, leaving offset two on disk. A fresh invocation loads that state and repeats the uncommitted work from the same pinned source. The final offset five and unique-id sum match a clean run. Compare complete state content, not only total, because an accidental offset change could otherwise go unnoticed. No external side effects exist in this lab beyond the single checkpoint publication.

## Exercise 6. Reject stale or corrupt state

A changed source produces a different snapshot identity, even when its parsed meaning happens to be similar. Refuse resume rather than silently resetting the checkpoint. A tampered total or offset also fails comparison with the expected prefix state. Parsing JSON verifies syntax only; state validation checks relationships among progress, source, aggregate, and completion. Preserve invalid state for inspection. Automatically deleting it would remove failure evidence and could cause replay under the wrong assumptions. The hash is an identity check, not a signature proving a trusted author.

## Exercise 7. Prove repeat and empty behavior

Once completion is true and the entire state matches its expected prefix, return it without rewriting. Byte-for-byte equality before and after a rerun makes that external idempotency visible. An empty source still needs a complete zero-row state so a caller can distinguish finished-empty from never-started. Reject bool, zero, and negative batch sizes before any write. Batch size changes how work is checkpointed, not the final aggregate. Try a different positive size on a fresh temporary checkpoint and compare its final state with the original.

## Exercise 8. Write an honest guarantee

The runbook should name the exact source identity, checkpoint location, ownership, resume command, next_row, completion flag, and aggregate checks. It should describe the injected failure and observed retained prefix. It must also say that concurrent writers, network filesystem semantics, directory fsync portability, physical disk loss, and external side effects were not tested or promised. That is not a weakness hidden in footnotes; it is the meaning of the evidence. Before broader deployment, choose mechanisms whose guarantees cover the actual failure and coordination model.

## Compare and transfer

Compare a clean run with a failed-and-resumed run across batch sizes one, two, and ten. Then describe what would break if two processes wrote the same checkpoint concurrently or if result files were published separately. Name the extra transaction or ownership mechanism needed before claiming those scenarios are handled.
