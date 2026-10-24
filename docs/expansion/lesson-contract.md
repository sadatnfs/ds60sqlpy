# A lesson contract that teaches

Status: proposed additive teaching schema. The current extension schema remains version 1. Planning JSON is version 1 of a separate design format, not an executable course manifest.

## Lesson shape

Every published lesson needs a clear purpose in a larger project, a prerequisite diagnostic, vocabulary, one mental model, two runnable worked examples, six distinct exercises, an explanation prompt, a retrieval task for a later session, and separate solutions. A beginner should see unfamiliar syntax explained before using it. An advanced learner should make a tradeoff and defend it with evidence.

| Phase | Learner action | Teacher response | Evidence |
| --- | --- | --- | --- |
| Orient | Choose an outcome and check prerequisite questions | Recommend a short bridge or direct entry | Diagnostic answers, editable route |
| Understand | Trace a small concrete example | Connect code, state, and the mental model | Annotated trace |
| Predict | Commit to an expected result before running | Explain differences after an attempt | Prediction text or choice |
| Experiment | Modify or construct a solution | Offer incremental hints on request | Source, input hashes, attempt receipt |
| Inspect | Read output, failure, metrics, or cluster state | Explain what the verifier actually checked | Verifier results and limits |
| Explain | State why it worked and one counterexample | Give a rubric and sample reasoning | Learner explanation, self-assessment |
| Review | Solve a changed problem later | Resurface weak concepts without erasing progress | New retrieval attempt |

Do not require a learner to write a meaningless sentence simply to unlock a button. Predictions and explanations should target the lesson's misconception. Self-reported confidence, machine verification, and teacher/human review are different signals and must be labelled independently.

## Exercises and hints

The six exercises should normally include tracing, a small modification, debugging, constructing a solution, an edge case, and transfer to a new situation. This is a teaching guideline, not a reason to force a nonsensical task into every lesson. Each exercise names exact inputs, expected observations, verification, failure interpretation, and at least three hints where useful. Hints progress from concept to strategy to concrete next step. Solutions require an explicit reveal and explain reasoning, not just final code.

Examples and fixtures must be small enough to inspect. Use deterministic tiny data before large datasets, one process before distributed workers, and fixed reference mathematics before stochastic training. Explain numerical tolerance, nondeterminism, ordering, and eventual state where exact equality is wrong. Include deliberate, safe failures that teach diagnosis.

## Verification types

| Type | Example | Required limits |
| --- | --- | --- |
| Exact result | C++ ownership test or deterministic Python scalar | Input, expected value, exception/exit behavior |
| Numerical tolerance | Gradient, attention matrix, tiny training metric | dtype, seed, absolute/relative tolerance; never loose enough to accept NaN |
| Invariant | Causal prefix invariance or row bag preservation | Positive and negative fixtures, no reliance on accidental ordering |
| Artifact | Model serialization, Parquet schema, compiled binary | Path allowlist, size, format/version, semantic reload |
| Eventual state | Deployment becomes Ready and serves expected content | Ownership, bounded polling deadline, conditions/events and endpoint probe |
| Recovery | Spark restart or Kubernetes reconciliation | Controlled disruption, before/after state, explicit cleanup |
| Performance | Spark partition or C++ allocation experiment | Recorded environment and repeated measurement; no universal millisecond threshold |
| Explanation | Leakage, ownership, masking, consistency tradeoffs | Transparent rubric and human/self review label |

A verifier must reject the relevant misconception. Test it with a known bad solution, an edge case, and its reference solution. Unit tests for the verifier cannot substitute for running the learner path. Do not grade prose with keyword matching and call that understanding. Optional future AI feedback needs opt-in, clear data boundaries, cost visibility, and offline alternatives; it is not part of this phase.

## Future structured metadata

An eventual schema 2 can add `objectives`, `diagnostic`, ordered `teaching_steps`, stable `exercises`, typed `verification`, `artifacts`, `review`, `accessibility`, and `runtime_requirements`. A registered verifier ID maps to trusted implementation code. Content cannot embed commands that obtain host privileges. Keep guide text canonical Markdown, and render it in the browser with the current safe document renderer.

Prerequisites also need explicit alternatives before publishing branch routes. For example, a Spark entry gate can accept demonstrated Scala foundations OR the PySpark bridge, while requiring the common environment lesson in both routes. The design format currently has AND-only edges; the Scala/Spark plan states its alternative competency gate in prose and does not claim the graph enforces it. A future prerequisite expression must define AND/OR semantics, cycle detection across all branches, learner overrides, and recommendation explanations.

Before adopting schema 2, implement an adapter for all existing schema-1 lessons, round-trip tests, explicit unknown-field errors, and a migration guide. The current strict loader will reject new fields, so adding them to active manifests today would break the course. Planned lessons stay under `docs/expansion/plans/` until their source artifacts and compatible runner exist.

## Author review checklist

1. Can a learner explain the objective and start without an unexplained prerequisite chain?
2. Do two examples reveal different aspects of the model?
3. Are all six exercises distinct, with usable inputs and checkable outcomes?
4. Does a wrong but plausible solution fail the intended check?
5. Are claims about runtime, architecture, offline assets, and resources backed by execution receipts?
6. Does the lesson work with keyboard navigation, narrow screens, readable output, and text alternatives?
7. Are references primary sources with review dates, and are downloadable fixtures licensed?
8. Can a learner resume after cancelling a job or replacing the application container?
